# 🎨 Image Editor Advanced - User Quick Guide

## 🚀 Getting Started

### Accessing the Editor
1. **Via Menu**: Left Sidebar → "Dashboards & Tools" → Click "Image Editor"
2. **Direct URL**: `http://localhost:3000/image-editor`
3. **Keyboard**: Press `E` (if hotkey enabled)

## 🛠️ Tools & Features

### Top Toolbar
- **Open**: Load image from file
- **Undo**: Revert last action (Ctrl+Z)
- **Redo**: Restore undone action (Ctrl+Y)
- **Zoom In**: Increase canvas zoom (+)
- **Zoom Out**: Decrease canvas zoom (-)
- **Export PNG**: Save as PNG file
- **Export JPG**: Save as JPG file

### Left Tool Panel (10 Tools)

#### 1. **Select Tool** (Grid3X3 icon)
- Select and manipulate objects
- Click tool to activate

#### 2. **Pan/Hand Tool** (Hand icon)
- Click and drag to move canvas
- Use for navigation

#### 3. **Brush Tool** (Paintbrush icon) ⭐
- Free-hand drawing
- Uses brush color and size
- Adjustable opacity
- Smooth stroke rendering

#### 4. **Eraser Tool** (Eraser icon) ⭐
- Remove parts of current layer
- Adjustable size
- Smooth erasing

#### 5. **Pencil Tool** (Pencil icon)
- Hard-edge drawing
- Precise lines

#### 6. **Crop Tool** (Crop icon)
- Crop image to selection
- Rectangular cropping

#### 7. **Color Picker** (Pipette icon)
- Select color from canvas
- Updates brush color

#### 8. **Shapes Tool** (Square/Circle)
- Draw rectangles, circles, lines
- Uses brush color

#### 9. **Text Tool** (Type icon)
- Add text to image
- Configurable font and size

#### 10. **Filters Tool** (Filter icon)
- Apply visual effects
- Real-time preview

### Right Panels

#### Layers Panel
- **Add Layer** (+): Create new layer
- **Layer List**: Show all layers
  - Click to select layer
  - Eye icon: Toggle visibility
  - Lock icon: Lock/unlock editing
  - X: Delete layer
- **Layer Properties**:
  - Name: Rename layer
  - Opacity: Layer transparency (0-100%)
  - Blend mode: Blending method

#### Adjustments Panel
- **Brightness**: 0-200% (100% = normal)
- **Contrast**: 0-200% (100% = normal)
- **Saturation**: 0-200% (100% = normal)
- **Blur**: 0-20px
- **Rotation**: 0-360°

#### Brush Settings Panel
- **Color**: Current brush color (click to change)
- **Size**: Brush diameter (1-100px)
- **Opacity**: Brush transparency (0-100%)
- **Preview**: Live brush preview

## 📋 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `+` | Zoom in |
| `-` | Zoom out |
| `B` | Brush tool |
| `E` | Eraser tool |
| `H` | Hand/pan tool |
| `C` | Color picker |
| `T` | Text tool |

## 🎯 Common Workflows

### Drawing on Canvas
1. Select **Brush Tool**
2. Choose color in Brush Settings
3. Set brush size (1-100px)
4. Adjust opacity if needed
5. Click and drag on canvas to draw
6. Use Undo if mistake

### Multi-Layer Editing
1. Click **Add Layer** button
2. Select layer in Layers panel
3. Draw on that layer only
4. Adjust layer opacity with slider
5. Lock layer when done editing

### Image Adjustments
1. Select image layer
2. Adjust sliders in Adjustments panel:
   - Brightness: Lighten/darken
   - Contrast: Increase/decrease detail
   - Saturation: More/less color
   - Blur: Soften edges
   - Rotation: Rotate image
3. Changes apply in real-time

### Creating Complex Artwork
1. Add multiple layers
2. Sketch on first layer (low opacity)
3. Draw details on next layer
4. Add effects on adjustment layer
5. Merge down when satisfied

### Exporting Finished Work
1. Click **Export PNG** for lossless quality
2. Or click **Export JPG** for smaller file
3. File downloads automatically
4. No quality loss from PNG
5. JPG more compressed but slight quality loss

## 🎨 Design Tips

### Color Theory
- **Warm colors**: Red, orange, yellow (energetic)
- **Cool colors**: Blue, green, purple (calming)
- **Complementary**: Opposite on color wheel (high contrast)
- **Analogous**: Adjacent on color wheel (harmonious)

### Brush Techniques
- **Large brush (50+px)**: Quick coverage, backgrounds
- **Medium brush (10-30px)**: General drawing
- **Small brush (1-10px)**: Details, fine lines
- **Low opacity (20-40%)**: Soft edges, blending
- **High opacity (80-100%)**: Solid strokes

### Layer Organization
- Name layers descriptively
- Keep similar elements on same layer
- Lock finished layers to prevent accidents
- Use opacity for blending
- Group related layers together

## ⚙️ Advanced Features

### Undo/Redo System
- Full history for current session
- Limited to session (not saved)
- Each brush stroke saved separately
- Unlimited undo/redo depth

### Performance Tips
- Keep canvas size reasonable
- Limit layers to necessary items
- Disable visibility of unused layers
- Lower blur value for faster rendering
- Export when done to free memory

### Quality Export
- **PNG**: Best quality, larger file (use for web graphics)
- **JPG**: Smaller file, slight quality loss (use for photos)
- Both maintain resolution of canvas

## 🐛 Troubleshooting

### Canvas Not Responding
- Click on canvas first to focus
- Check if layer is locked
- Try selecting a different tool

### Changes Not Showing
- Verify layer is visible (eye icon)
- Check zoom level (might be zoomed in)
- Try refreshing adjustments

### Brush Not Drawing
- Verify Brush tool is selected
- Check brush color is not black on black
- Ensure layer is unlocked
- Try different brush size

### Export Not Working
- Check browser download permissions
- Try PNG instead of JPG
- Refresh page and retry
- Check browser console for errors

## 📊 Canvas Information
- **Max zoom**: 5x (500%)
- **Min zoom**: 0.1x (10%)
- **Brush size range**: 1-100px
- **Max layers**: Limited by browser memory
- **File format**: PNG (lossless) or JPG (lossy)

## 🔧 Settings
- **Theme**: Dark (default)
- **Default brush color**: Pink (#f472b6)
- **Default brush size**: 10px
- **Default opacity**: 100%
- **Auto-save**: Per session only

## 💾 File Management
- **Imports**: PNG, JPG, GIF, WebP
- **Exports**: PNG, JPG
- **Session**: Lost on page reload
- **Persistence**: Save to local file to preserve

## 🎓 Learning Resources
- Try each tool individually
- Experiment with brush sizes
- Test layer blending
- Practice with different images
- Combine tools for complex effects

## ⭐ Pro Tips

1. **Use layers for non-destructive editing**
2. **Zoom in for precise details**
3. **Adjust before exporting**
4. **Save frequently to external file**
5. **Use color picker to match existing colors**
6. **Lock layers to prevent accidents**
7. **Name layers for organization**
8. **Use opacity for subtle effects**
9. **Combine multiple adjustments**
10. **Export in appropriate format for use**

---

**Happy Editing!** 🎨✨

For more information, check the Advanced section in the documentation.
