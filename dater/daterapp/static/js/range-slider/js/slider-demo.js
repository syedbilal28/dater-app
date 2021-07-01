/* =======================================================================
 * slider-demo.js
 * Version: 1.0
 * Date: 2016/04/29
 * By: Rich DeBourke
 * License: MIT
 * GitHub: https://github.com/RichDeBourke/mouse-touch-range-slider
 * RGB to HSV based on: http://www.javascripter.net/faq/rgb2hsv.htm
 * HSV to RGB based on: http://snipplr.com/view/14590
 * ======================================================================= */

(function ($, document) {
    "use strict";
    var hexVal;
    var cRVal;
    var cGVal;
    var cBVal;
    var cHValHolder = "0";
    var cSValHolder = "0";
    var cVValHolder = "0";
    var rSliderHandle;
    var gSliderHandle;
    var bSliderHandle;
    var hSliderHandle;
    var rSliderElement;
    var gSliderElement;
    var bSliderElement;
    var hSliderElement;
    var $colorResult;

    function hexValid(strHexValue) {
        var result = false;

        strHexValue = strHexValue.toUpperCase();
        if (/^[0-9A-F]{3}$|^[0-9A-F]{6}$/.test(strHexValue)) {
            result = strHexValue;
            if (strHexValue.length === 3) {
                result = strHexValue.charAt(0) + strHexValue.charAt(0) + strHexValue.charAt(1) + strHexValue.charAt(1) + strHexValue.charAt(2) + strHexValue.charAt(2);
            }
        }
        return result;
    }

    function decimalValid(valueDecimalValue) {
        var result = false;

        if (/^\d+$/.test(valueDecimalValue)) {
            result = true;
        }
        return result;
    }

    // Polyfill for Number.isNan (from MDN) as IE doesn't support the function
    Number.isNaN = Number.isNaN || function isNaN(input) {
        return typeof input === "number" && input !== input;
    };

    function hex(x) {
        var arrayHexDigits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"];

        return (
            Number.isNaN(x)
            ? "00"
            : arrayHexDigits[(x - x % 16) / 16] + arrayHexDigits[x % 16]);
    }

    function updateRGBfromHex() {
        var hexColor = hexVal.value;

        if (cRVal.value !== parseInt(hexColor.substring(0, 2), 16).toString()) {
            cRVal.value = parseInt(hexColor.substring(0, 2), 16);
        }
        if (cGVal.value !== parseInt(hexColor.substring(2, 4), 16).toString()) {
            cGVal.value = parseInt(hexColor.substring(2, 4), 16);
        }
        if (cBVal.value !== parseInt(hexColor.substring(4, 6), 16).toString()) {
            cBVal.value = parseInt(hexColor.substring(4, 6), 16);
        }
    }

    function updateHexFromRGB() {
        hexVal.value = hex(cRVal.value) + hex(cGVal.value) + hex(cBVal.value);
    }

    function updateHSVfromRGB() {
        var d;
        var h;
        var hsvH;
        var hsvS;
        var hsvV;
        var minRGB;
        var maxRGB;
        var cR;
        var cG;
        var cB;

        cR = cRVal.value / 255;
        cG = cGVal.value / 255;
        cB = cBVal.value / 255;
        minRGB = Math.min(cR, Math.min(cG, cB));
        maxRGB = Math.max(cR, Math.max(cG, cB));
        if (maxRGB === minRGB) {
            hsvH = 0;
            hsvS = 0;
            hsvV = maxRGB;
        } else {
            d = ((cR === minRGB) ? cG - cB : ((cB === minRGB) ? cR - cG : cB - cR));
            h = ((cR === minRGB) ? 3 : ((cB === minRGB) ? 1 : 5));
            hsvH = 60 * (h - d / (maxRGB - minRGB));
            hsvS = (maxRGB - minRGB) / maxRGB;
            hsvV = maxRGB;
        }
        if (cHValHolder !== Math.round(hsvH).toString()) {
            cHValHolder = Math.round(hsvH).toString();
        }
        if (cSValHolder !== Math.round(hsvS * 100).toString()) {
            cSValHolder = Math.round(hsvS * 100).toString();
        }
        if (cVValHolder !== Math.round(hsvV * 100).toString()) {
            cVValHolder = Math.round(hsvV * 100).toString();
        }
    }

    function updateRGBfromHSV() {
        var tmp;
        var factorial;
        var p;
        var q;
        var t;
        var H;
        var S;
        var V;

        H = parseInt(cHValHolder, 10);
        S = parseInt(cSValHolder, 10) / 100;
        V = parseInt(cVValHolder, 10) / 100;

        if (S === 0) {
            tmp = Math.round(V * 255);
            cRVal.value = tmp.toString();
            cGVal.value = tmp.toString();
            cBVal.value = tmp.toString();
        } else {
            if (H === 360) {
                H = 0;
            }
            H = H / 60;
            tmp = Math.floor(H);
            factorial = H - tmp; // factorial part of h
            p = V * (1 - S);
            q = V * (1 - S * factorial);
            t = V * (1 - S * (1 - factorial));
            switch (tmp) {
            case 0:
                cRVal.value = Math.round(V * 255).toString();
                cGVal.value = Math.round(t * 255).toString();
                cBVal.value = Math.round(p * 255).toString();
                break;
            case 1:
                cRVal.value = Math.round(q * 255).toString();
                cGVal.value = Math.round(V * 255).toString();
                cBVal.value = Math.round(p * 255).toString();
                break;
            case 2:
                cRVal.value = Math.round(p * 255).toString();
                cGVal.value = Math.round(V * 255).toString();
                cBVal.value = Math.round(t * 255).toString();
                break;
            case 3:
                cRVal.value = Math.round(p * 255).toString();
                cGVal.value = Math.round(q * 255).toString();
                cBVal.value = Math.round(V * 255).toString();
                break;
            case 4:
                cRVal.value = Math.round(t * 255).toString();
                cGVal.value = Math.round(p * 255).toString();
                cBVal.value = Math.round(V * 255).toString();
                break;
            default: // case 5:
                cRVal.value = Math.round(V * 255).toString();
                cGVal.value = Math.round(p * 255).toString();
                cBVal.value = Math.round(q * 255).toString();
            }
        }
    }

    function updateSliderPositions() {
        // Values in the text boxes are calculated
        // Sliders are updated only if the value has changed

        if (rSliderElement.value !== cRVal.value) {
            rSliderHandle.update(cRVal.value);
        }
        if (gSliderElement.value !== cGVal.value) {
            gSliderHandle.update(cGVal.value);
        }
        if (bSliderElement.value !== cBVal.value) {
            bSliderHandle.update(cBVal.value);
        }
        if (hSliderElement.value !== cHValHolder) {
            hSliderHandle.update(cHValHolder);
        }

    }

    function updateRGBfromSliders(sliderId) {
        switch (sliderId) {
        case rSliderElement.id:
            cRVal.value = rSliderElement.value;
            break;
        case gSliderElement.id:
            cGVal.value = gSliderElement.value;
            break;
        default:
            cBVal.value = bSliderElement.value;
        }
    }

    function updateHSVfromSliders() {
        if (cHValHolder !== hSliderElement.value) {
            cHValHolder = hSliderElement.value;
        }
    }

    function getLuminance(rgb) {
        var i;
        var lum;

        for (i = 0; i < rgb.length; i++) {
            if (rgb[i] <= 0.03928) {
                rgb[i] = rgb[i] / 12.92;
            } else {
                rgb[i] = Math.pow(((rgb[i] + 0.055) / 1.055), 2.4);
            }
        }
        lum = (0.2126 * rgb[0]) + (0.7152 * rgb[1]) + (0.0722 * rgb[2]);
        return lum;
    }

    function updateColorsDisplay() {
        var cRi = parseInt(cRVal.value, 10);
        var cGi = parseInt(cGVal.value, 10);
        var cBi = parseInt(cBVal.value, 10);
        var lumForInitial;

        $colorResult.css("background-color", "#" + hexVal.value);

        lumForInitial = getLuminance([cRi / 255, cGi / 255, cBi / 255]);

        if ((lumForInitial > 0.215) && ($colorResult.css("color") === "rgb(255, 255, 255)")) {
            $colorResult.css("color", "#000000");
        } else if ((lumForInitial <= 0.215) && ($colorResult.css("color") === "rgb(0, 0, 0)")) {
            $colorResult.css("color", "#FFFFFF");
        }
    }

    function hexInputBoxChanged(event) {
        var validHexInput = hexValid(event.currentTarget.value);

        if (validHexInput) {
            event.currentTarget.value = validHexInput;
            updateRGBfromHex();
            updateHSVfromRGB();
            updateColorsDisplay();
            updateSliderPositions();
        } else {
            updateHexFromRGB();
        }
    }

    function rgbInputBoxChanged(event) {
        var value = parseInt(event.currentTarget.value, 10);

        if (decimalValid(event.currentTarget.value) && (value >= 0 && value <= 255)) {
            event.currentTarget.value = value.toString();
            updateHexFromRGB();
            updateHSVfromRGB();
            updateColorsDisplay();
            updateSliderPositions();
        } else {
            updateRGBfromHex();
        }
    }

    function rgbSliderMoved(sliderDataObject) {
        updateRGBfromSliders(sliderDataObject.id);
        updateHexFromRGB();
        updateHSVfromRGB();
        updateColorsDisplay();
        updateSliderPositions();
    }

    function hsvSliderMoved() {
        updateHSVfromSliders();
        updateRGBfromHSV();
        updateHexFromRGB();
        updateColorsDisplay();
        updateSliderPositions();
    }


    /* Setup the document objects:
        Set the hex field and the three decimal fields to their initial values
            and bind a function to handle changes to the values
        Create the sliders and set them to an initial value. */
    $(document).ready(function () {
        $(".color-slider").mtRangeSlider({
            min: 0,
            max: 255,
            onChange: rgbSliderMoved
        });
        $(".hue-slider").mtRangeSlider({
            min: 0,
            max: 360,
            onChange: hsvSliderMoved
        });
        // Handles for positioning Sliders
        rSliderHandle = $("#c-red").data("mtRangeSlider");
        gSliderHandle = $("#c-green").data("mtRangeSlider");
        bSliderHandle = $("#c-blue").data("mtRangeSlider");
        hSliderHandle = $("#c-hue").data("mtRangeSlider");
        // Handles for getting SliderHandle values
        rSliderElement = document.getElementById("c-red");
        gSliderElement = document.getElementById("c-green");
        bSliderElement = document.getElementById("c-blue");
        hSliderElement = document.getElementById("c-hue");
        // Set the initial values to the input boxes and bind the change handlers
        $("#hex-c").val("0024A7").on("focus", function () {this.select();}).change(hexInputBoxChanged);
        $("#c-r").val("0").on("focus", function () {this.select();}).change(rgbInputBoxChanged);
        $("#c-g").val("36").on("focus", function () {this.select();}).change(rgbInputBoxChanged);
        $("#c-b").val("167").on("focus", function () {this.select();}).change(rgbInputBoxChanged);
        cHValHolder = "227";
        cSValHolder = "100";
        cVValHolder = "65";
        // Handles for getting & setting the values for the color the input boxes
        hexVal = document.getElementById("hex-c");
        cRVal = document.getElementById("c-r");
        cGVal = document.getElementById("c-g");
        cBVal = document.getElementById("c-b");
        // jQuery handles for setting the background and text colors for the two color table divs
        $colorResult = $("#color-result");
        updateColorsDisplay();
        updateSliderPositions();

    });
}(jQuery, document));
