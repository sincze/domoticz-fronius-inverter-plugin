-----------------------

# domoticz-fronius-inverter-plugin
Domoticz Fronius Inverter plugin
--------------------------------

This version of the plugin is running on my Domoticz 2023.1.
Based on the great work of: Auke De Jong

It creates 2 devices on the Utility page.
One custom meter showing only the current generated Watts.
The other is a kWh type meter

Modify inverter so it will stay awake during the night. 
This can be done via the Fronisus portal.

Installation
------------

In your `domoticz/plugins` directory do

```bash
git clone https://github.com/aukedejong/domoticz-fronius-inverter-plugin.git
```

Restart your Domoticz service with:

```bash
sudo service domoticz.sh restart
```

Now go to **Setup**, **Hardware** in Domoticz. There you add
**Fronius Inverter**.

Fill in the IP address and device ID.
For me the device ID is 1.

Currently the plugin only supports Fronius API version 1

Feature to add
--------------

- Debug options.
- Option to select which devices should be created
- Option the disable the fraction calculation feature
- Detection of Fronius API version
- Some things I can't remember now.

This plugin uses an icon by 
<a href="https://www.flaticon.com/authors/vectors-market" title="Vectors Market">
Vectors Market</a> from 
<a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>
and is licensed by 
<a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">
CC 3.0 BY</a>
