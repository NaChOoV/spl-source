import httpx
from httpx import Cookies, Response, Timeout

from datetime import datetime
from config.env import config
from app.mappers.access_mappers import AccessDataMapper
import re
import json
import logging
from app.models.access_model import Access
from app.models.user import AbmUser, User, UserAccess
from typing import Callable, Awaitable

from utils.decorators import singleton
from bs4 import BeautifulSoup, Tag

from utils.date_format import format_chilean_date_time_to_utc


@singleton
class SourceService:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._base_url: str = config.SOURCE_BASE_URL
        self._cookies: Cookies | None = None
        self._proxy = None

        if config.HTTP_PROXY:
            self._proxy = config.HTTP_PROXY
            self._logger.info(f"Using proxies: {self._proxy}")

        self._timeout = Timeout(
            connect=15.0,  # Timeout para establecer conexión
            read=45.0,  # Timeout para leer respuesta
            write=15.0,  # Timeout para escribir datos
            pool=15.0,  # Timeout para obtener conexión del pool
        )

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers={"user-agent": ""},
            proxy=self._proxy,
            cookies=self._cookies,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def login(self) -> Response:
        form_data = {"LOGIN": config.SOURCE_USERNAME, "CLAVE": config.SOURCE_PASSWORD}

        response = await self._client.post("login_servidor.php", data=form_data)

        if not response.json()["estado"]["sesion"]:
            raise Unauthorized("Login failed - invalid credentials")

        self._cookies = response.cookies
        self._logger.info("Logged in successfully")

        return response

    async def _retry_with_login[T](
        self, operation_func: Callable[[], Awaitable[T]], max_retries: int = 3
    ) -> T:
        """
        Retry an operation after re-authenticating.

        Args:
            operation_func: Async function to retry after login
            max_retries: Maximum number of retry attempts

        Returns:
            Result of the operation function

        Raises:
            Unauthorized: If login fails or max retries exceeded
        """
        for attempt in range(max_retries + 1):
            try:
                self._logger.info(
                    f"Attempting to re-authenticate (attempt {attempt + 1}/{max_retries + 1})"
                )

                # Attempt to login
                login_response = await self.login()

                if not login_response.json()["estado"]["sesion"]:
                    raise Unauthorized("Login failed - invalid credentials")

                # Retry the original operation with new session
                return await operation_func()

            except (httpx.RequestError, KeyError, json.JSONDecodeError) as e:
                self._logger.warning(f"Retry attempt {attempt + 1} failed: {str(e)}")

                if attempt == max_retries:
                    self._logger.error(
                        f"All retry attempts exhausted after {max_retries + 1} tries"
                    )
                    raise Unauthorized(
                        f"Authentication retry failed after {max_retries + 1} attempts: {str(e)}"
                    )

            except Exception as e:
                self._logger.error(f"Unexpected error during retry: {str(e)}")
                raise e

        # This should never be reached due to the exception handling above
        raise Unauthorized(
            f"Authentication retry failed after {max_retries + 1} attempts"
        )

    async def get_today_access(self) -> list[Access]:
        """
        Internal method to get today's access data that can be retried.
        """
        today = datetime.now().strftime("%Y-%m-%d")

        form_data = {
            "QUERY": "ACCESOS",
            "DATOSFORM": f"FECHAINI={today}&FECHAFIN={today}",
        }
        response = await self._client.post(
            "main_servidor.php",
            data=form_data,
        )

        try:
            response_data = response.json()
            if response_data.get("sesion") is False:
                return await self._retry_with_login(self.get_today_access)
        except Exception as e:
            raise e

        html_content = response.json()["html"]

        match = re.search(r"tablaReser\s*=\s*(\[.*?\]);", html_content, re.DOTALL)
        if match:
            # Extract the array content
            array_content = match.group(1)
            # Clean and parse the JSON
            try:
                raw_data = json.loads(array_content)
                return AccessDataMapper.map_access_records(raw_data)
            except json.JSONDecodeError:
                raise ParseException("Error parsing JSON")
            except Exception as e:
                raise e
        else:
            self._logger.error("No access data match found on the html body")
            return []

    async def get_abm_user_by_run(self, run: str) -> AbmUser | None:
        """
        Get the user information from the ABM system.

        Returns:
            AbmUser | None: The user information or None if not found
        """
        response = await self._client.get(
            f"/abm/abm_socios.php?CONTACTOCAMPO7={run.upper()}",
        )

        try:
            response_data = response.text
            if response_data == "OPCION DISPONIBLE SOLO PARA ADMINISTRADORES":
                return await self._retry_with_login(
                    lambda: self.get_abm_user_by_run(run)
                )
        except Exception as e:
            raise e

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="listado")
        if not table:
            return None

        if not table or not isinstance(table, Tag):
            return None

        tbody = table.find("tbody")
        if not tbody or not isinstance(tbody, Tag):
            return None

        rows = tbody.find_all("tr")
        if not rows:
            return None

        # Process the first row to extract user data
        first_row = rows[0]

        if not isinstance(first_row, Tag):
            return None
        cells = first_row.find_all("td")
        cell_run = cells[1].get_text(strip=True).upper() if cells[1] else ""

        if cell_run != run.upper():
            return None

        external_id = cells[0].get_text(strip=True) if cells[0] else ""
        last_name = cells[2].get_text(strip=True) if cells[2] else ""
        first_name = cells[3].get_text(strip=True) if cells[3] else ""

        return AbmUser(
            run=run.upper(),
            first_name=first_name,
            last_name=last_name,
            external_id=int(external_id),
        )

    async def get_user_by_external_id(self, external_id: int):
        """
        Get the user information from the system.

        Returns:
            User | None: The user information or None if not found
        """
        form_data = {
            "QUERY": "VERPERFIL",
            "IDCONTACTO": external_id,
        }

        response = await self._client.post(
            "main_servidor.php",
            data=form_data,
        )

        try:
            response_data = response.json()
            if response_data.get("sesion") is False:
                return await self._retry_with_login(
                    lambda: self.get_user_by_external_id(external_id)
                )
        except Exception as e:
            raise e

        html_str = str(response.json()["html"])

        if "Contacto no encontrado" in html_str:
            return None

        return extract_user_info(html_str)

    async def get_inbody_by_external_id(self, external_id: int) -> list[str]:
        """
        Get list of in-body information for a user by external ID.

        Returns:
            list[str]: The in-body information or an empty list if not found
        """
        form_data = {
            "QUERY": "ADJUNTARARCHIVOINBODY",
            "IDCONTACTO": external_id,
        }

        response = await self._client.post(
            "main_servidor.php",
            data=form_data,
        )

        try:
            response = response.json()
            if response.get("sesion") is False:
                return await self._retry_with_login(
                    lambda: self.get_inbody_by_external_id(external_id)
                )
        except Exception as e:
            raise e

        html_str = str(response["html"])

        if "No se encontró la carpeta de registros" in html_str:
            return []

        soup = BeautifulSoup(html_str, "html.parser")
        # Find the panel containing uploaded files
        uploaded_files_panel = soup.find("div", class_="archivosSubidos")
        if not uploaded_files_panel or not isinstance(uploaded_files_panel, Tag):
            return []

        # Find the panel body containing the file links
        panel_body = uploaded_files_panel.find("div", class_="panel-body")
        if not panel_body or not isinstance(panel_body, Tag):
            return []

        # Extract all anchor tags with href attributes
        file_links = []
        links = panel_body.find_all("a", href=True)

        for link in links:
            if isinstance(link, Tag):
                href = link.get("href")
                if href and isinstance(href, str):
                    # Convert relative URLs to absolute URLs
                    if href.startswith("uploads_inbody/"):
                        full_url = f"{self._base_url}/{href}"
                        file_links.append(full_url)
                    elif href.startswith("http"):
                        # Already absolute URL
                        file_links.append(href)

        return list(reversed(file_links))


class ParseException(Exception):
    pass


class Unauthorized(Exception):
    pass


def extract_user_info(html_str: str) -> User | None:
    soup = BeautifulSoup(html_str, "html.parser")

    # Extract image URL from img tag with name attribute (not id)
    image_url: str | None = None
    image_element = soup.find("img")
    if image_element and isinstance(image_element, Tag):
        # The image URL is in the 'name' attribute, not 'src'
        src = str(image_element.get("name", ""))
        if src and src.startswith("https://storage.googleapis.com/"):
            image_url = src

    # Extract first and last name from JSON data in admin comment
    first_name = ""
    last_name = ""
    run = ""

    # Look for the admin comment containing JSON data
    admin_comment = soup.find("span", class_="adminComment")
    if admin_comment and isinstance(admin_comment, Tag):
        comment_text = admin_comment.get_text()
        # Extract JSON part after "CONTACTO: "
        if "CONTACTO: " in comment_text:
            json_part = comment_text.split("CONTACTO: ", 1)[1]
            try:
                contact_data = json.loads(json_part)
                first_name = contact_data.get("CONTACTOCAMPO2", "")
                last_name = contact_data.get("CONTACTOCAMPO1", "")
                run = contact_data.get("CONTACTOCAMPO7", "")
            except json.JSONDecodeError:
                # Fallback: try to extract using regex
                first_name_match = re.search(r'"CONTACTOCAMPO2":"([^"]*)"', json_part)
                last_name_match = re.search(r'"CONTACTOCAMPO1":"([^"]*)"', json_part)
                run_match = re.search(r'"CONTACTOCAMPO7":"([^"]*)"', json_part)
                if first_name_match:
                    first_name = first_name_match.group(1)
                if last_name_match:
                    last_name = last_name_match.group(1)
                if run_match:
                    run = run_match.group(1)

    # Extract access history from "Historial de Accesos" table
    access_history = []

    # Find all tables and look for one containing access history
    tables = soup.find_all("table")
    for table in tables:
        if not isinstance(table, Tag):
            continue

        # Look for table headers that indicate this is the access history
        headers = table.find_all("th")
        header_texts = [
            th.get_text(strip=True).lower() for th in headers if isinstance(th, Tag)
        ]

        # Check if this looks like an access history table
        # Look for the specific column headers: Fecha, Sede, Actividad, Registro
        if any(
            all(
                col in " ".join(header_texts)
                for col in ["fecha", "sede", "actividad", "registro"]
            )
            for header_texts in [header_texts]
        ) or "historial de accesos" in " ".join(header_texts):
            tbody = table.find("tbody")
            if tbody and isinstance(tbody, Tag):
                rows = tbody.find_all("tr")
                for row in rows:
                    if not isinstance(row, Tag):
                        continue

                    cells = row.find_all("td")
                    if (
                        len(cells) >= 4
                    ):  # Ensure we have at least Fecha, Sede, Actividad, Registro columns
                        # Column order: Fecha, Sede, Actividad, Registro
                        # Extract location from Sede column (index 1)
                        date_text = cells[0].get_text(strip=True) if cells[0] else ""

                        location_text = (
                            cells[1].get_text(strip=True) if cells[1] else ""
                        )
                        try:
                            location_id = int(
                                AccessDataMapper._map_location(location_text)
                            )
                        except (ValueError, TypeError):
                            location_id = 0

                        registro_text = (
                            cells[3].get_text(strip=True) if cells[3] else ""
                        )
                        entry_time = ""
                        exit_time = None

                        if registro_text:
                            # Split by space to get entry and exit times
                            time_parts = registro_text.split()
                            entry_time = time_parts[0] + ":00"
                            if len(time_parts) >= 2:
                                exit_time = time_parts[1] + ":00"

                        user_access = UserAccess(
                            location=location_id,
                            entry_at=format_chilean_date_time_to_utc(
                                date_text, entry_time
                            ),
                            exit_at=None
                            if not exit_time
                            else format_chilean_date_time_to_utc(date_text, exit_time),
                        )
                        access_history.append(user_access)
            break  # Found the access table, no need to check others

    return User(
        image_url=image_url,
        run=run,
        first_name=first_name,
        last_name=last_name,
        access_history=access_history,
    )
