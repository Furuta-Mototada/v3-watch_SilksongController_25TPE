package com.example.grid_watch_udp_datacollector

import android.content.Context
import android.content.SharedPreferences
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

class DataCollectorViewModel : ViewModel() {

    // Action types
    val actions = listOf("WALK", "IDLE", "PUNCH", "JUMP", "TURN_LEFT", "TURN_RIGHT")

    // State for button counts
    val actionCounts = mutableStateMapOf<String, Int>().apply {
        actions.forEach { this[it] = 0 }
    }

    // State for currently recording action
    val recordingAction = mutableStateOf<String?>(null)

    // State for server IP
    val serverIP = mutableStateOf("192.168.10.234")

    // State for connection status
    val connectionStatus = mutableStateOf("Not connected")

    // UDP settings
    private val UDP_PORT = 12345
    private val PREFS_NAME = "ButtonDataCollector"
    private val IP_ADDRESS_KEY = "server_ip_address"
    private val COUNT_PREFIX = "count_"

    private var sharedPreferences: SharedPreferences? = null

    fun initialize(context: Context) {
        sharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        loadSavedData()
    }

    private fun loadSavedData() {
        sharedPreferences?.let { prefs ->
            // Load IP address
            serverIP.value = prefs.getString(IP_ADDRESS_KEY, "192.168.10.234") ?: "192.168.10.234"

            // Load counts for each action
            actions.forEach { action ->
                actionCounts[action] = prefs.getInt("$COUNT_PREFIX$action", 0)
            }
        }
    }

    fun saveIpAddress(ip: String) {
        if (isValidIpAddress(ip)) {
            serverIP.value = ip
            sharedPreferences?.edit()?.putString(IP_ADDRESS_KEY, ip)?.apply()
        }
    }

    private fun saveCount(action: String, count: Int) {
        sharedPreferences?.edit()?.putInt("$COUNT_PREFIX$action", count)?.apply()
    }

    fun onButtonPressed(action: String) {
        if (recordingAction.value != null) {
            // Already recording something, ignore
            return
        }

        recordingAction.value = action
        val timestamp = System.currentTimeMillis()

        // Send label_start event
        sendLabelEvent(action, "start", timestamp)
    }

    fun onButtonReleased(action: String) {
        if (recordingAction.value != action) {
            // Not recording this action, ignore
            return
        }

        recordingAction.value = null
        val timestamp = System.currentTimeMillis()

        // Increment count
        val newCount = (actionCounts[action] ?: 0) + 1
        actionCounts[action] = newCount
        saveCount(action, newCount)

        // Send label_end event with updated count
        sendLabelEvent(action, "end", timestamp, newCount)
    }

    private fun sendLabelEvent(action: String, event: String, timestamp: Long, count: Int? = null) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                val jsonPayload = if (count != null) {
                    """{"type":"label_event","action":"${action.lowercase()}","event":"$event","timestamp_ms":$timestamp,"count":$count}"""
                } else {
                    """{"type":"label_event","action":"${action.lowercase()}","event":"$event","timestamp_ms":$timestamp}"""
                }

                sendUdpMessage(jsonPayload)
            } catch (e: Exception) {
                android.util.Log.e("DataCollector", "Error sending label event", e)
            }
        }
    }

    private fun sendUdpMessage(message: String) {
        try {
            val socket = DatagramSocket()
            val messageBytes = message.toByteArray()
            val serverAddress = InetAddress.getByName(serverIP.value)
            val packet = DatagramPacket(messageBytes, messageBytes.size, serverAddress, UDP_PORT)
            socket.send(packet)
            socket.close()

            // Update connection status on success
            viewModelScope.launch(Dispatchers.Main) {
                connectionStatus.value = "Connected to ${serverIP.value}"
            }
        } catch (e: Exception) {
            android.util.Log.e("UDP_SENDER", "Error sending packet", e)
            viewModelScope.launch(Dispatchers.Main) {
                connectionStatus.value = "Error: ${e.message}"
            }
        }
    }

    fun resetCounts() {
        actions.forEach { action ->
            actionCounts[action] = 0
            saveCount(action, 0)
        }
    }

    fun testConnection() {
        // Send a test ping message to verify connection
        viewModelScope.launch(Dispatchers.IO) {
            try {
                val testMessage = """{"type":"label_event","action":"test","event":"ping","timestamp_ms":${System.currentTimeMillis()}}"""
                sendUdpMessage(testMessage)
                viewModelScope.launch(Dispatchers.Main) {
                    connectionStatus.value = "Test ping sent to ${serverIP.value}"
                }
            } catch (e: Exception) {
                android.util.Log.e("DataCollector", "Test connection failed", e)
            }
        }
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

    fun getCountColor(count: Int): androidx.compose.ui.graphics.Color {
        return when {
            count < 10 -> androidx.compose.ui.graphics.Color(0xFFF44336) // Red
            count < 30 -> androidx.compose.ui.graphics.Color(0xFFFFC107) // Yellow/Amber
            else -> androidx.compose.ui.graphics.Color(0xFF4CAF50) // Green
        }
    }
}
