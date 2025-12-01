# Assets Folder

## Logo Instructions

Please add your logo file here with the name: **logo.png**

Supported formats:
- PNG (recommended): `logo.png`
- JPG/JPEG: `logo.jpg` or `logo.jpeg`
- SVG: `logo.svg`

### Requirements:
- Recommended size: 200x200 pixels or similar square/rectangular dimensions
- Transparent background (PNG) works best
- The logo will be displayed at 50px height (scales automatically)

### If your logo has a different name:
Update the import in `/frontend/src/LandingPage.js` line 14:
```javascript
src={require('./assets/YOUR_LOGO_NAME.png')}
```

### If your logo is in a different format:
Change the file extension in the require statement accordingly:
```javascript
src={require('./assets/logo.svg')}  // for SVG
src={require('./assets/logo.jpg')}  // for JPG
```


