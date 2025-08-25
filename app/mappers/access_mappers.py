"""
Data mappers for transforming source system data to application format.
"""

from typing import Any
from app.const.enum import Location, LocationStr
from app.models.access_model import Access
from datetime import datetime
from utils.date_format import format_chilean_date_time_to_utc


class AccessDataMapper:
    """Mapper for access data from source system"""

    @staticmethod
    def _map_location(location_name: str) -> str:
        """
        Map location name to structured location object with ID and name.

        Args:
            location_name: Raw location name from source system

        Returns:
            LocationModel object with location id and name
        """
        # Create a mapping from LocationStr values to Location values
        location_mapping = {
            LocationStr.ESPACIO_URBANO.value: Location.ESPACIO_URBANO.value,
            LocationStr.CALAMA.value: Location.CALAMA.value,
            LocationStr.PACIFICO.value: Location.PACIFICO.value,
            LocationStr.ARAUCO.value: Location.ARAUCO.value,
            LocationStr.IQUIQUE.value: Location.IQUIQUE.value,
            LocationStr.ANGAMOS.value: Location.ANGAMOS.value,
        }

        # Find the location ID based on the name
        location_id = location_mapping.get(
            location_name, 0
        )  # Default to 0 if not found

        return str(location_id)

    @staticmethod
    def map_access_records(raw_data: list[dict[str, Any]]) -> list[Access]:
        """
        Map raw access data to Access model objects.

        Args:
            raw_data: List of raw access records from the source system

        Returns:
            List of Access model objects
        """
        mapped_data = []

        for record in raw_data:
            date = (
                record.get("FECHA")
                if record.get("FECHA")
                else datetime.now().strftime("%Y-%m-%d")
            )

            entry_at = str(record.get("TURNOINI"))
            exit_at = (
                None if not record.get("TURNOFIN") else str(record.get("TURNOFIN"))
            )

            access_record = Access(
                external_id=record.get("IDCONTACTO", 0),
                run=record.get("RUT", ""),
                full_name=record.get("SOCIO", ""),
                entry_at=format_chilean_date_time_to_utc(date, entry_at),
                exit_at=None
                if not exit_at
                else format_chilean_date_time_to_utc(date, exit_at),
                activity=record.get("ACTIVIDAD", ""),
                location=AccessDataMapper._map_location(record.get("SEDE", "")),
            )
            mapped_data.append(access_record)

        return mapped_data
