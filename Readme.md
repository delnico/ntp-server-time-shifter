# NTP server - special implementation

This NTP server was created for experimental purposes.

It returns a time that is intended to be incorrect,
Its functions are to be requested by others servers that need a time marker like CA server.
It is used to highlight problems encountered when using certificates with different times, or uses time for synchronization, ...

The implementation consists of causing a time shift: one real hour will be equivalent to one second on the server (by default).

See ntp-server.service to enable script as a service using systemd.

## Environment

- Tested on Ubuntu Server 22.04.5 LTS
- Python 3.10.12

## Testing

```shell
ntpdate -q <ip>
```
