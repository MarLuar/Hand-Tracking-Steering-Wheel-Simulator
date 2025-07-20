# Hand Tracking Steering Wheel Simulator

A real-time hand tracking application that converts hand gestures into steering wheel controls for driving games. Using computer vision and gesture recognition, this simulator lets you control vehicles in games using natural hand movements captured by your webcam.

## Features

- **Real-time Hand Tracking**: Uses Google's MediaPipe for accurate hand detection and tracking
- **Steering Control**: Hand angle between wrists controls left/right steering
- **Throttle/Brake**: Thumb gestures control acceleration and braking
- **Visual Feedback**: Live camera feed with hand landmarks and control status
- **Performance Monitoring**: Real-time FPS display and angle measurements
- **Dead Zone Filtering**: Prevents jittery inputs with configurable dead zones

## Demo

The application tracks both hands simultaneously:
- **Steering**: Tilt your hands left or right to steer
- **Accelerate**: Thumbs up with left hand
- **Brake**: Thumbs up with right hand
- **Neutral**: Keep fists closed for no throttle input

## Requirements

- Python 3.7+
- Webcam (camera index 0)
- Good lighting conditions for hand detection

### Dependencies

Install the required packages:

```bash
pip install opencv-python mediapipe pyautogui
```

Or create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install opencv-python mediapipe pyautogui
```

## Installation

1. Clone or download this repository
2. Install dependencies (see above)
3. Ensure your webcam is connected and working
4. Run the application

## Usage

### Running the Simulator

```bash
python "Hand Tracking Steering Wheel Simulator.py"
```

### Controls

| Action | Gesture | Key Output |
|--------|---------|------------|
| Steer Left | Tilt hands left | 'a' key |
| Steer Right | Tilt hands right | 'd' key |
| Accelerate | Left thumb up | 'w' key |
| Brake | Right thumb up | 's' key |
| Stop/Neutral | Closed fists | No input |

### Configuration

You can adjust these parameters in the code:

- `DEAD_ZONE_ANGLE = 20`: Minimum angle before steering activates (degrees)
- `MAX_ANGLE = 60`: Maximum steering angle for full lock (degrees)
- `STEERING_SMOOTHING = 0`: Smoothing factor (0-1, currently disabled)

### Exiting

Press 'q' in the OpenCV window to quit the application.

## How It Works

1. **Camera Input**: Captures video from your webcam at 640x480 resolution
2. **Hand Detection**: MediaPipe identifies and tracks both hands in real-time
3. **Gesture Recognition**: 
   - Calculates angle between left and right hand wrists for steering
   - Detects thumb position relative to hand for throttle/brake
4. **Input Mapping**: Converts gestures to keyboard inputs (WASD keys)
5. **Visual Feedback**: Displays camera feed with hand landmarks and status

## Technical Details

- **Computer Vision**: OpenCV for camera handling and display
- **Hand Tracking**: MediaPipe Hands model with optimized settings
- **Input Automation**: PyAutoGUI for keyboard control
- **Performance**: Optimized for real-time operation with FPS monitoring

## Troubleshooting

### Common Issues

**Hand detection not working:**
- Ensure good lighting conditions
- Keep hands clearly visible in camera view
- Try adjusting `min_detection_confidence` and `min_tracking_confidence` values

**Laggy or choppy performance:**
- Close other applications using the camera
- Reduce camera resolution if needed
- Check that your system meets performance requirements

**Game not responding to inputs:**
- Make sure the game window is active and accepts WASD inputs
- Some games may require specific input settings
- Test keyboard inputs manually first

### Advanced Configuration

For developers wanting to modify the behavior:

- **Recovery System**: Currently disabled, can be enabled by setting `RECOVERY_FACTOR` and `RECOVERY_DURATION` > 0
- **Steering Smoothing**: Increase `STEERING_SMOOTHING` (0-1) for smoother steering
- **Hand Detection**: Adjust MediaPipe parameters for different accuracy/performance trade-offs

## Compatible Games

This simulator works with any game that accepts WASD keyboard inputs for driving:
- Racing simulators (Assetto Corsa, BeamNG.drive, etc.)
- Open-world games with vehicles (GTA, Forza Horizon, etc.)
- Browser-based driving games

## Limitations

- Requires consistent lighting for reliable hand detection
- May have latency depending on system performance
- Works best with games that support analog-style keyboard input
- Requires both hands to be visible for steering control

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the simulator.

## Acknowledgments

- Google MediaPipe team for the hand tracking solution
- OpenCV community for computer vision tools