var dispFont = new FontFace('D14MR', 'url("/fonts/DSEG14-Classic/DSEG14Classic-Regular.woff")');
dispFont.load().then(function(loadedFace) {
	document.fonts.add(loadedFace);
	document.body.style.fontFamily = '"D14MR", Electrolize';
}).catch(function(error) {
});

