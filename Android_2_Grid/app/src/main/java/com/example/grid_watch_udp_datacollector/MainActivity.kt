package com.example.grid_watch_udp_datacollector

import android.content.Context
import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.grid_watch_udp_datacollector.ui.theme.Grid_Watch_UDP_DataCollectorTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            Grid_Watch_UDP_DataCollectorTheme {
                DataCollectorScreen()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DataCollectorScreen(viewModel: DataCollectorViewModel = viewModel()) {
    val context = LocalContext.current
    val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator

    // Initialize ViewModel with context
    LaunchedEffect(Unit) {
        viewModel.initialize(context)
    }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = { Text("Button Data Collector") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Black,
                    titleContentColor = Color.White
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // Button Grid - Takes up entire first screen
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .padding(16.dp)
            ) {
                ButtonGrid(
                    viewModel = viewModel,
                    onVibrate = { duration ->
                        if (vibrator.hasVibrator()) {
                            vibrator.vibrate(
                                VibrationEffect.createOneShot(duration, VibrationEffect.DEFAULT_AMPLITUDE)
                            )
                        }
                    }
                )
            }

            // Everything else below (user can scroll down)
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Connection Status
                Text(
                    text = viewModel.connectionStatus.value,
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (viewModel.connectionStatus.value.startsWith("Connected"))
                        Color(0xFF4CAF50) else Color(0xFFF44336),
                    modifier = Modifier.fillMaxWidth(),
                    textAlign = TextAlign.Center
                )

                // IP Configuration Section
                IpConfigSection(viewModel)

                // Action Buttons Row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Test Connection Button
                    Button(
                        onClick = { viewModel.testConnection() },
                        modifier = Modifier
                            .weight(1f)
                            .height(50.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF2C2C2C) // Dark gray
                        )
                    ) {
                        Text(
                            text = "Connect",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = Color.White.copy(alpha = 0.9f)
                        )
                    }

                    // Reset Button
                    Button(
                        onClick = { viewModel.resetCounts() },
                        modifier = Modifier
                            .weight(1f)
                            .height(50.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFFF6B6B) // Soft red
                        )
                    ) {
                        Text(
                            text = "Reset",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun IpConfigSection(viewModel: DataCollectorViewModel) {
    var ipInput by remember { mutableStateOf(viewModel.serverIP.value) }
    var showDialog by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Server IP: ${viewModel.serverIP.value}",
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Bold
            )

            Button(
                onClick = { showDialog = true },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Change IP Address")
            }
        }
    }

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false },
            title = { Text("Enter Server IP") },
            text = {
                OutlinedTextField(
                    value = ipInput,
                    onValueChange = { ipInput = it },
                    label = { Text("IP Address") },
                    placeholder = { Text("192.168.1.100") }
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.saveIpAddress(ipInput)
                        showDialog = false
                    }
                ) {
                    Text("Save")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
fun ButtonGrid(viewModel: DataCollectorViewModel, onVibrate: (Long) -> Unit) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Row 1: WALK, IDLE
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ActionButton(
                action = "WALK",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
            ActionButton(
                action = "IDLE",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
        }

        // Row 2: PUNCH, JUMP
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ActionButton(
                action = "PUNCH",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
            ActionButton(
                action = "JUMP",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
        }

        // Row 3: TURN_LEFT, TURN_RIGHT
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ActionButton(
                action = "TURN_LEFT",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
            ActionButton(
                action = "TURN_RIGHT",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
fun ActionButton(
    action: String,
    viewModel: DataCollectorViewModel,
    onVibrate: (Long) -> Unit,
    modifier: Modifier = Modifier
) {
    val count = viewModel.actionCounts[action] ?: 0
    val isRecording = viewModel.recordingAction.value == action

    // Dark sophisticated color palette inspired by banking app
    val backgroundColor = when {
        isRecording -> Color(0xFF1E1E1E) // Very dark gray when recording
        else -> when (action) {
            "WALK" -> Color(0xFF2C2C2C) // Dark charcoal
            "IDLE" -> Color(0xFF2E2E2E) // Dark gray
            "PUNCH" -> Color(0xFF3A2B2B) // Dark brown-red
            "JUMP" -> Color(0xFF2F2F2F) // Dark neutral
            "TURN_LEFT" -> Color(0xFF2A2D2E) // Dark blue-gray
            "TURN_RIGHT" -> Color(0xFF302A2E) // Dark purple-gray
            else -> Color(0xFF2B2B2B) // Dark fallback
        }
    }

    // Subtle accent colors for recording state
    val accentColor = when (action) {
        "WALK" -> Color(0xFF4A90E2) // Soft blue
        "IDLE" -> Color(0xFF9B9B9B) // Light gray
        "PUNCH" -> Color(0xFFE74C3C) // Soft red
        "JUMP" -> Color(0xFFF39C12) // Soft orange
        "TURN_LEFT" -> Color(0xFF3498DB) // Light blue
        "TURN_RIGHT" -> Color(0xFFE91E63) // Soft pink
        else -> Color(0xFF95A5A6) // Gray accent
    }

    Card(
        modifier = modifier
            .aspectRatio(1f)
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        // Button pressed
                        viewModel.onButtonPressed(action)
                        onVibrate(50) // Short vibration

                        // Wait for release (non-blocking)
                        val released = tryAwaitRelease()

                        // Button released
                        if (released) {
                            viewModel.onButtonReleased(action)
                            onVibrate(100) // Longer vibration on release
                        }
                    }
                )
            },
        elevation = CardDefaults.cardElevation(defaultElevation = if (isRecording) 8.dp else 2.dp),
        colors = CardDefaults.cardColors(containerColor = backgroundColor)
    ) {
        Box(
            modifier = Modifier.fillMaxSize()
        ) {
            // Subtle gradient overlay when recording
            if (isRecording) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(accentColor.copy(alpha = 0.2f))
                )
            }

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(12.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = action.replace("_", " "),
                    fontSize = 16.sp,
                    fontWeight = if (isRecording) FontWeight.Bold else FontWeight.Medium,
                    color = if (isRecording) accentColor else Color.White.copy(alpha = 0.9f),
                    textAlign = TextAlign.Center,
                    lineHeight = 18.sp
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = "$count",
                    fontSize = 24.sp,
                    color = if (isRecording) accentColor else Color.White.copy(alpha = 0.6f),
                    fontWeight = FontWeight.Light
                )
            }
        }
    }
}