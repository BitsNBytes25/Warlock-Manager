from typing_extensions import deprecated
from warlock_manager.libs.ip import get_wan_ip as new_get_wan_ip


@deprecated('This functionality has moved to warlock_manager.libs.ip.get_wan_ip')
def get_wan_ip() -> str | None:
	return new_get_wan_ip()
