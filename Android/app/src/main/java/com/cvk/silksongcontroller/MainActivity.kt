package com.cvk.silksongcontroller

import android.Manifest // NEW: Import for permissions
import android.content.Context
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import android.view.WindowManager
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.widget.SwitchCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

class MainActivity : AppCompatActivity(), SensorEventListener {

    private lateinit var sensorManager: SensorManager
    private var rotationVectorSensor: Sensor? = null
    private var stepDetectorSensor: Sensor? = null
    // --- NEW: Add a property for the Linear Acceleration Sensor ---
    private var linearAccelerationSensor: Sensor? = null
    // --- NEW: Add a property for the Gyroscope Sensor ---
    private var gyroscopeSensor: Sensor? = null

    // --- NEW: Views for status feedback ---
    private lateinit var rotationStatusView: TextView
    private lateinit var stepStatusView: TextView
    // --- NEW: UI View for the new sensor ---
    private lateinit var accelStatusView: TextView
    // --- NEW: UI View for the gyroscope sensor ---
    private lateinit var gyroStatusView: TextView

    // --- NEW: IP address management ---
    private lateinit var ipAddressEditText: EditText
    private lateinit var saveIpButton: Button
    private lateinit var ipStatusTextView: TextView
    private lateinit var connectionStatusTextView: TextView
    private lateinit var sharedPreferences: SharedPreferences
    private var currentServerIP = "192.168.10.234" // Default IP

    private val UDP_PORT = 12345
    private val PREFS_NAME = "SilksongController"
    private val IP_ADDRESS_KEY = "server_ip_address"

    // --- NEW: Constant for the permission request ---
    private val ACTIVITY_RECOGNITION_REQUEST_CODE = 100

    // --- NSD (Network Service Discovery) ---
    private lateinit var nsdManager: NsdManager
    private var discoveryListener: NsdManager.DiscoveryListener? = null
    private var resolveListener: NsdManager.ResolveListener? = null
    private val SERVICE_TYPE = "_silksong._udp."
    private var isDiscovering = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize SharedPreferences
        sharedPreferences = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

        // Initialize UI components
        val streamSwitch: SwitchCompat = findViewById(R.id.switch_stream)
        rotationStatusView = findViewById(R.id.tv_status_rotation)
        stepStatusView = findViewById(R.id.tv_status_step)
        accelStatusView = findViewById(R.id.tv_status_accel)
        gyroStatusView = findViewById(R.id.tv_status_gyro)

        // Initialize IP management UI
        ipAddressEditText = findViewById(R.id.et_ip_address)
        saveIpButton = findViewById(R.id.btn_save_ip)
        ipStatusTextView = findViewById(R.id.tv_ip_status)
        connectionStatusTextView = findViewById(R.id.tv_connection_status)

        // Load saved IP address or use default
        loadSavedIpAddress()

        // Set up IP save button
        saveIpButton.setOnClickListener {
            saveIpAddress()
        }

        // Initialize NSD Manager
        nsdManager = getSystemService(Context.NSD_SERVICE) as NsdManager
        
        // Start service discovery
        startServiceDiscovery()

        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager

        // Initialize sensors, but don't use them yet
        rotationVectorSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)
        stepDetectorSensor = sensorManager.getDefaultSensor(Sensor.TYPE_STEP_DETECTOR)
        // --- NEW: Initialize the Linear Acceleration sensor ---
        linearAccelerationSensor = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)
        gyroscopeSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE) // Initialize the new sensor

        updateSensorStatusUI()

        streamSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                // --- MODIFIED: Check permissions before starting ---
                checkPermissionAndStartStreaming()
            } else {
                stopStreaming()
            }
        }
    }

    private fun checkPermissionAndStartStreaming() {
        // [Citation: https://developer.android.com/training/permissions/requesting]
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED) {
            // Permission is already granted, start streaming
            startStreaming()
        } else {
            // Permission is not granted, request it from the user
            requestPermissions(arrayOf(Manifest.permission.ACTIVITY_RECOGNITION), ACTIVITY_RECOGNITION_REQUEST_CODE)
        }
    }

    // --- NEW: This function handles the result of the permission request ---
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == ACTIVITY_RECOGNITION_REQUEST_CODE) {
            if ((grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED)) {
                // Permission was granted, now we can start streaming
                startStreaming()
            } else {
                // Permission was denied. Inform the user and disable the switch.
                Toast.makeText(this, "Permission denied. Step Detector will not work.", Toast.LENGTH_LONG).show()
                findViewById<SwitchCompat>(R.id.switch_stream).isChecked = false
                updateSensorStatusUI()
            }
        }
    }

    private fun updateSensorStatusUI() {
        rotationStatusView.text = if (rotationVectorSensor != null) "Rotation Vector: Ready" else "Rotation Vector: NOT AVAILABLE"
        accelStatusView.text = if (linearAccelerationSensor != null) "Linear Accel: Ready" else "Linear Accel: NOT AVAILABLE"
        gyroStatusView.text = if (gyroscopeSensor != null) "Gyroscope: Ready" else "Gyroscope: NOT AVAILABLE" // Update status for new sensor

        val hasPermission = ContextCompat.checkSelfPermission(this, Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED
        stepStatusView.text = when {
            stepDetectorSensor == null -> "Step Detector: NOT AVAILABLE"
            !hasPermission -> "Step Detector: PERMISSION NEEDED"
            else -> "Step Detector: Ready"
        }
    }

    private fun startStreaming() {
        // --- NEW: Add this line to keep the screen on ---
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        // --- MODIFIED: Register all sensors including the new linear acceleration sensor ---
        sensorManager.registerListener(this, rotationVectorSensor, SensorManager.SENSOR_DELAY_GAME)
        sensorManager.registerListener(this, linearAccelerationSensor, SensorManager.SENSOR_DELAY_GAME)
        sensorManager.registerListener(this, gyroscopeSensor, SensorManager.SENSOR_DELAY_GAME) // Register the new sensor

        // Only register the step detector if we have permission
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED) {
            sensorManager.registerListener(this, stepDetectorSensor, SensorManager.SENSOR_DELAY_NORMAL)
        }

        Toast.makeText(this, "Streaming ON", Toast.LENGTH_SHORT).show()
    }

    // The rest of the file remains largely the same
    private fun stopStreaming() {
        // --- NEW: Add this line to allow the screen to sleep again ---
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        sensorManager.unregisterListener(this)
        Toast.makeText(this, "Streaming OFF", Toast.LENGTH_SHORT).show()
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    override fun onSensorChanged(event: SensorEvent?) {
        when (event?.sensor?.type) {
            Sensor.TYPE_ROTATION_VECTOR -> {
                val values = event.values
                val jsonPayload = """{"sensor": "rotation_vector", "timestamp_ns": ${event.timestamp}, "values": {"x": ${values[0]}, "y": ${values[1]}, "z": ${values[2]}, "w": ${values.getOrNull(3) ?: 0.0}}}"""
                sendData(jsonPayload)
            }
            Sensor.TYPE_STEP_DETECTOR -> {
                val jsonPayload = """{"sensor": "step_detector", "timestamp_ns": ${event.timestamp}}"""
                sendData(jsonPayload)
            }
            // --- NEW: Handle events from the Linear Accelerometer ---
            Sensor.TYPE_LINEAR_ACCELERATION -> {
                val values = event.values
                val jsonPayload = """{"sensor": "linear_acceleration", "timestamp_ns": ${event.timestamp}, "values": {"x": ${values[0]}, "y": ${values[1]}, "z": ${values[2]}}}"""
                sendData(jsonPayload)
            }
            // --- NEW: Handle events from the Gyroscope ---
            Sensor.TYPE_GYROSCOPE -> {
                val values = event.values
                val jsonPayload = """{"sensor": "gyroscope", "timestamp_ns": ${event.timestamp}, "values": {"x": ${values[0]}, "y": ${values[1]}, "z": ${values[2]}}}"""
                sendData(jsonPayload)
            }
        }
    }

    private fun sendData(jsonPayload: String) {
        lifecycleScope.launch(Dispatchers.IO) { sendUdpMessage(jsonPayload) }
    }

    private fun sendUdpMessage(message: String) {
        try {
            val socket = DatagramSocket()
            val messageBytes = message.toByteArray()
            val serverAddress = InetAddress.getByName(currentServerIP)
            val packet = DatagramPacket(messageBytes, messageBytes.size, serverAddress, UDP_PORT)
            socket.send(packet)
            socket.close()
        } catch (e: Exception) {
            Log.e("UDP_SENDER", "Error sending packet", e)
        }
    }

    private fun loadSavedIpAddress() {
        currentServerIP = sharedPreferences.getString(IP_ADDRESS_KEY, "192.168.10.234") ?: "192.168.10.234"
        ipAddressEditText.setText(currentServerIP)
        updateIpStatusDisplay()
    }

    private fun saveIpAddress() {
        val newIpAddress = ipAddressEditText.text.toString().trim()

        if (isValidIpAddress(newIpAddress)) {
            currentServerIP = newIpAddress

            // Save to SharedPreferences
            with(sharedPreferences.edit()) {
                putString(IP_ADDRESS_KEY, currentServerIP)
                apply()
            }

            updateIpStatusDisplay()
            Toast.makeText(this, "IP address saved: $currentServerIP", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "Invalid IP address format", Toast.LENGTH_SHORT).show()
        }
    }

    private fun updateIpStatusDisplay() {
        ipStatusTextView.text = "Current IP: $currentServerIP"
    }

    private fun isValidIpAddress(ip: String): Boolean {
        return try {
            val parts = ip.split(".")
            if (parts.size != 4) return false

            for (part in parts) {
                val num = part.toInt()
                if (num < 0 || num > 255) return false
            }
            true
        } catch (e: NumberFormatException) {
            false
        }
    }

    private fun startServiceDiscovery() {
        if (isDiscovering) {
            return
        }

        discoveryListener = object : NsdManager.DiscoveryListener {
            override fun onDiscoveryStarted(serviceType: String) {
                Log.d("NSD", "Service discovery started")
                isDiscovering = true
                runOnUiThread {
                    connectionStatusTextView.text = "Searching..."
                    connectionStatusTextView.setTextColor(getColor(android.R.color.holo_orange_light))
                }
            }

            override fun onServiceFound(serviceInfo: NsdServiceInfo) {
                Log.d("NSD", "Service found: ${serviceInfo.serviceName}")
                if (serviceInfo.serviceType == SERVICE_TYPE && 
                    serviceInfo.serviceName.contains("SilksongController")) {
                    // Resolve the service to get IP and port
                    resolveService(serviceInfo)
                }
            }

            override fun onServiceLost(serviceInfo: NsdServiceInfo) {
                Log.d("NSD", "Service lost: ${serviceInfo.serviceName}")
                runOnUiThread {
                    connectionStatusTextView.text = "Connection Lost"
                    connectionStatusTextView.setTextColor(getColor(android.R.color.holo_red_light))
                }
            }

            override fun onDiscoveryStopped(serviceType: String) {
                Log.d("NSD", "Discovery stopped")
                isDiscovering = false
            }

            override fun onStartDiscoveryFailed(serviceType: String, errorCode: Int) {
                Log.e("NSD", "Discovery failed: Error code: $errorCode")
                nsdManager.stopServiceDiscovery(this)
                isDiscovering = false
            }

            override fun onStopDiscoveryFailed(serviceType: String, errorCode: Int) {
                Log.e("NSD", "Stop discovery failed: Error code: $errorCode")
                nsdManager.stopServiceDiscovery(this)
                isDiscovering = false
            }
        }

        try {
            nsdManager.discoverServices(SERVICE_TYPE, NsdManager.PROTOCOL_DNS_SD, discoveryListener)
        } catch (e: Exception) {
            Log.e("NSD", "Failed to start discovery", e)
            Toast.makeText(this, "Failed to start service discovery", Toast.LENGTH_SHORT).show()
        }
    }

    private fun resolveService(serviceInfo: NsdServiceInfo) {
        resolveListener = object : NsdManager.ResolveListener {
            override fun onResolveFailed(serviceInfo: NsdServiceInfo, errorCode: Int) {
                Log.e("NSD", "Resolve failed: $errorCode")
            }

            override fun onServiceResolved(serviceInfo: NsdServiceInfo) {
                Log.d("NSD", "Service resolved: ${serviceInfo.serviceName}")
                
                val host = serviceInfo.host
                val port = serviceInfo.port
                
                // Update IP address
                currentServerIP = host.hostAddress ?: currentServerIP
                
                runOnUiThread {
                    // Update UI
                    connectionStatusTextView.text = "Connected!"
                    connectionStatusTextView.setTextColor(getColor(android.R.color.holo_green_light))
                    ipAddressEditText.setText(currentServerIP)
                    updateIpStatusDisplay()
                    
                    Toast.makeText(
                        this@MainActivity,
                        "Found server at $currentServerIP:$port",
                        Toast.LENGTH_LONG
                    ).show()
                    
                    Log.d("NSD", "Server IP: $currentServerIP, Port: $port")
                }
            }
        }

        try {
            nsdManager.resolveService(serviceInfo, resolveListener)
        } catch (e: Exception) {
            Log.e("NSD", "Failed to resolve service", e)
        }
    }

    private fun stopServiceDiscovery() {
        if (isDiscovering && discoveryListener != null) {
            try {
                nsdManager.stopServiceDiscovery(discoveryListener!!)
            } catch (e: Exception) {
                Log.e("NSD", "Failed to stop discovery", e)
            }
        }
    }

    override fun onPause() {
        super.onPause()
        stopStreaming()
    }

    override fun onDestroy() {
        super.onDestroy()
        stopServiceDiscovery()
    }
}
