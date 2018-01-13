request = b"""NOTIFY * HTTP/1.1
Host: 239.255.255.250:1982
Cache-Control: max-age=3600
Location: yeelight://192.168.1.239:55443
NTS: ssdp:alive
Server: POSIX, UPnP/1.0 YGLC/1
id: 0x000000000015243f
model: color
fw_ver: 18
support: get_prop set_default set_power toggle set_bright start_cf stop_cf set_scene cron_add cron_get cron_del set_ct_abx set_rgb
power: on
bright: 100
color_mode: 2
ct: 4000
rgb: 16711680
hue: 100
sat: 35
name: my_bulb""".replace(b'\n', b'\r\n')

response = b"""HTTP/1.1 200 OK
Cache-Control: max-age=3600
Date:
Ext:
Location: yeelight://192.168.1.239:55443
Server: POSIX UPnP/1.0 YGLC/1
id: 0x000000000015243f
model: color
fw_ver: 18
support: get_prop set_default set_power toggle set_bright start_cf stop_cf set_scene cron_add cron_get cron_del set_ct_abx set_rgb
power: on
bright: 100
color_mode: 2
ct: 4000
rgb: 16711680
hue: 100
sat: 35
name: my_bulb""".replace(b'\n', b'\r\n')

response_wrong_location = b"""HTTP/1.1 200 OK
Cache-Control: max-age=3600
Date:
Ext:
Location: yeelight://not.an.ip:55443
Server: POSIX UPnP/1.0 YGLC/1""".replace(b'\n', b'\r\n')
