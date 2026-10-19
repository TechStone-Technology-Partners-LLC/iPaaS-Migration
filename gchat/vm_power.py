"""Deallocate the Azure VM this bot runs on (idle shutdown).

Uses the VM's own managed identity through the instance metadata endpoint —
no credentials on disk. The identity needs a role on the VM that allows
Microsoft.Compute/virtualMachines/deallocate/action (Virtual Machine
Contributor scoped to the VM). See docs/how-migraite-bot-works/migraite-wake-on-message.md §3.

Deallocate (not an OS shutdown) is what stops compute billing.
"""

import requests

IMDS = "http://169.254.169.254/metadata"
ARM = "https://management.azure.com"
_HDR = {"Metadata": "true"}


def _vm_identity() -> tuple[str, str, str]:
    """(subscription, resource group, vm name) of the machine we're on."""
    r = requests.get(f"{IMDS}/instance/compute", params={"api-version": "2021-02-01"},
                     headers=_HDR, timeout=5)
    r.raise_for_status()
    m = r.json()
    return m["subscriptionId"], m["resourceGroupName"], m["name"]


def _arm_token() -> str:
    r = requests.get(f"{IMDS}/identity/oauth2/token",
                     params={"api-version": "2018-02-01", "resource": f"{ARM}/"},
                     headers=_HDR, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def deallocate_self() -> None:
    """Ask Azure to deallocate this VM. Returns once the request is accepted;
    the OS is shut down shortly after, which ends this process."""
    sub, rg, name = _vm_identity()
    url = (f"{ARM}/subscriptions/{sub}/resourceGroups/{rg}"
           f"/providers/Microsoft.Compute/virtualMachines/{name}/deallocate")
    r = requests.post(url, params={"api-version": "2024-07-01"},
                      headers={"Authorization": f"Bearer {_arm_token()}"}, timeout=30)
    if r.status_code not in (200, 202):
        raise RuntimeError(f"deallocate refused: HTTP {r.status_code} {r.text[:300]}")
