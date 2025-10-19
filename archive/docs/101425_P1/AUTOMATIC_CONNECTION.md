# Automatic Connection Feature

## Overview

The Silksong Watch Controller now features automatic device discovery using Network Service Discovery (NSD), eliminating the need for manual IP address configuration. This "magic link" enables seamless connection between the Wear OS device and the host computer.

## How It Works

### 1. Service Advertisement (Python Host)

The Python host (`udp_listener.py`) automatically advertises itself on the local network using the `zeroconf` library:

```python
from zeroconf import ServiceInfo, Zeroconf

# Service registration
zeroconf = Zeroconf()
service_type = "_silksong._udp.local."
service_name = f"SilksongController.{service_type}"

service_info = ServiceInfo(
    service_type,
    service_name,
    addresses=[socket.inet_aton(LISTEN_IP)],
    port=LISTEN_PORT,
    properties={"version": "1.0"},
)

zeroconf.register_service(service_info)
```

**Key Points:**
- Service type: `_silksong._udp.local.` (custom mDNS service)
- Service name: `SilksongController._silksong._udp.local.`
- Broadcasts on local network using multicast DNS (mDNS/Bonjour protocol)
- Includes IP address, port (12345), and metadata

### 2. Service Discovery (Android Client)

The Android app uses `NsdManager` to discover the advertised service:

```kotlin
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo

// Initialize NSD Manager
nsdManager = getSystemService(Context.NSD_SERVICE) as NsdManager

// Start discovery
nsdManager.discoverServices(
    "_silksong._udp.",
    NsdManager.PROTOCOL_DNS_SD,
    discoveryListener
)
```

**Discovery Flow:**
1. `onDiscoveryStarted()` - Starts scanning for services
2. `onServiceFound()` - Detects the SilksongController service
3. Service resolution - Obtains IP address and port
4. `onServiceResolved()` - Updates UI and stores connection details

### 3. Connection Status UI

The watch app displays real-time connection status:

```xml
<TextView
    android:id="@+id/tv_connection_status"
    android:text="Searching..."
    android:textColor="#FFA500" />
```

**Status States:**
- 🟠 **"Searching..."** (Orange) - Actively discovering services
- 🟢 **"Connected!"** (Green) - Service found and resolved
- 🔴 **"Connection Lost"** (Red) - Service unavailable

## Implementation Details

### Files Modified

1. **requirements.txt**
   - Added: `zeroconf>=0.131.0`

2. **src/udp_listener.py**
   - Imported `ServiceInfo` and `Zeroconf`
   - Added service registration after socket binding
   - Added cleanup in `finally` block to unregister service

3. **Android/app/src/main/AndroidManifest.xml**
   - Added `ACCESS_NETWORK_STATE` permission
   - Added `CHANGE_WIFI_MULTICAST_STATE` permission

4. **Android/app/src/main/java/com/cvk/silksongcontroller/MainActivity.kt**
   - Imported `NsdManager` and `NsdServiceInfo`
   - Added NSD-related properties
   - Implemented `startServiceDiscovery()` method
   - Implemented `resolveService()` method
   - Implemented `stopServiceDiscovery()` method
   - Added automatic IP update when service is discovered
   - Added connection status TextView updates

5. **Android/app/src/main/res/layout/activity_main.xml**
   - Added connection status TextView at the top of the layout

## Network Requirements

For automatic discovery to work:

1. **Same Network**: Both devices must be on the same local network (WiFi)
2. **mDNS Support**: Network router must support multicast DNS (most home routers do)
3. **Firewall**: Multicast traffic must not be blocked
4. **Port Availability**: UDP port 12345 must be available on the host

## Fallback Options

Manual IP configuration is still available:

1. If automatic discovery fails, users can manually enter the IP address
2. The IP address field and "Save" button remain functional
3. Saved IP addresses persist across app restarts

## Testing

### Python Side Test
```bash
# Test zeroconf service registration
python -c "
import socket
from zeroconf import ServiceInfo, Zeroconf
zc = Zeroconf()
info = ServiceInfo(
    '_silksong._udp.local.',
    'Test._silksong._udp.local.',
    addresses=[socket.inet_aton('127.0.0.1')],
    port=12345
)
zc.register_service(info)
print('Service registered')
zc.unregister_service(info)
zc.close()
"
```

### Android Side
1. Build and install the app on a Wear OS device
2. Start the Python controller on the same network
3. Watch the connection status change from "Searching..." to "Connected!"
4. Verify the IP address field is automatically populated

## Troubleshooting

### Service Not Discovered

**Problem**: Watch stays on "Searching..."

**Solutions:**
1. Verify both devices are on the same WiFi network
2. Check firewall settings on the host computer
3. Restart the Python controller
4. Use manual IP entry as fallback

### Service Registration Failed

**Problem**: Python script fails to start

**Solutions:**
1. Ensure `zeroconf` library is installed: `pip install zeroconf`
2. Check that port 12345 is not already in use
3. Verify network interface is available

### Permission Denied

**Problem**: Android app crashes on startup

**Solutions:**
1. Grant network permissions in Android settings
2. Reinstall the app
3. Check Android version compatibility (minSdk: 26)

## Future Enhancements

Potential improvements:
- Multiple server support
- Service version checking
- Automatic reconnection on connection loss
- Connection quality indicators
- Service discovery timeout configuration

## References

- [Android NSD Guide](https://developer.android.com/training/connect-devices-wirelessly/nsd)
- [zeroconf Python Library](https://github.com/python-zeroconf/python-zeroconf)
- [mDNS/Bonjour Protocol](https://tools.ietf.org/html/rfc6762)
