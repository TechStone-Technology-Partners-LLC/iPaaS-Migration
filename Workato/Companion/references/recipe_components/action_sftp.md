# Action: SFTP

SFTP actions manage files on a remote SFTP server. A stored SFTP connection is required
(host, port, username, password or key).

---

## stat (Check if File Exists)

```python
step_sftp_stat = {
    "number": N,
    "keyword": "action",
    "provider": "sftp",
    "name": "stat",
    "as": "check_file",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "path": "/incoming/"
                + dp("workato_service", "trig", "filename")
    }
}
```

### Output

```python
dp("sftp", "check_file", "exists")       # boolean — True if file found
dp("sftp", "check_file", "size")         # integer — file size in bytes
dp("sftp", "check_file", "last_modified") # timestamp
```

---

## download / get (Read File Content)

```python
step_sftp_download = {
    "number": N,
    "keyword": "action",
    "provider": "sftp",
    "name": "download_file",
    "as": "read_file",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "path": "/incoming/" + dp("workato_service", "trig", "filename")
    }
}

# Access file content
dp("sftp", "read_file", "file_content")
```

---

## upload (Write File to SFTP)

```python
step_sftp_upload = {
    "number": N,
    "keyword": "action",
    "provider": "sftp",
    "name": "upload_file",
    "as": "upload_output",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {
        "append": False    # False = overwrite; True = append to existing file
    },
    "input": {
        "path": "/outgoing/" + dp("workato_service", "trig", "outputFilename"),
        "content": dp("workato_service", "trig", "fileContent"),
        "append": False
    }
}
```

### toggleCfg for upload

`"append": False` must appear in `toggleCfg`. Without it, Workato defaults to append
mode and the `append` key in `input` is ignored.

---

## rename (Move or Rename a File)

```python
step_sftp_rename = {
    "number": N,
    "keyword": "action",
    "provider": "sftp",
    "name": "rename_file",
    "as": "archive_file",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "source_path": "/incoming/" + dp("workato_service", "trig", "filename"),
        "destination_path": "/archive/" + dp("workato_service", "trig", "filename")
    }
}
```

---

## remove (Delete a File)

```python
step_sftp_remove = {
    "number": N,
    "keyword": "action",
    "provider": "sftp",
    "name": "remove_file",
    "as": "delete_processed",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "path": "/incoming/" + dp("workato_service", "trig", "filename")
    }
}
```

---

## Datapill Pattern for Dynamic Paths

Build file paths dynamically using datapills mixed with static path strings:

```python
"path": "/data/"
        + dp("workato_service", "trig", "subfolder")
        + "/"
        + dp("workato_service", "trig", "filename")
        + ".csv"
```

---

## Config Entry

```python
{"keyword": "application", "provider": "sftp", "account_id": 88421, "skip_validation": False}
```

Replace `88421` with the actual SFTP connection ID from `workato-connection-list.py`.

---

## Notes

- All paths are absolute on the SFTP server (start with `/`).
- The SFTP connection must be authorised in Workato GUI with host, port, and credentials.
- For the `new_file` trigger (polling SFTP for new arrivals), use provider `sftp` with
  name `new_file` — this is configured manually in the GUI after pushing the trigger stub.
