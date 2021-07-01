/* =======================================================================
 * jquery.mtRangeSlider.js
 * Version: 1.2
 * Date: 2021/01/01
 * By: Rich DeBourke
 * License: MIT
 * GitHub: https://github.com/RichDeBourke/mouse-touch-range-slider
 * ======================================================================= */

(function ($, win, doc) {
    "use strict";

    var mouseTouchRangeSlider = function (element, options) {
        var config = [];
        var result = [];

        var sourceInput = element; // reference to the source element
        var $sourceInput = $(element); // reference to the jQuery version of the source
        var $rsContainer = null;
        var $track = null;
        var $slider = null;

        var plugin = this;

        if ($sourceInput.prop("tabindex")) {
            config.tabIndex = $sourceInput.prop("tabindex");
        } else {
            config.tabIndex = 0;
        }

        // measurement variables
        config.containerWidth = 0; // Width of the span with the unique plugin ID
        config.sliderWidth = 0; // Width of the handle
        config.containerLeftOffset = 0; // Distance from the left side of the window to the container (for mouse positioning)
        config.containerTravelPixels = 0; // # of pixels for traveling
        config.containerTravelPercentage = 0; // % of the container for traveling
        config.fullRange = 0; // How many steps
        config.oneStepPixels = 0; // How many pixels represent one step (usually a fraction of a pixel)
        config.oneStepPercentage = 0; // % of the container travel distance representing one step
        config.absolutePixelPointer = 0; // Pixel distance to the left side of slider for the current value
        config.fuzzyPixelPointer = 0; // Distance from left side to where the mouse was first clicked on the slider

        // default config
        config.options = {
            min: 0,
            max: 100,
            step: 1,
            initialValue: 0,
            keyboard: true,
            onCreate: null,
            onStart: null,
            onChange: null,
            onFinish: null
        };

        result = {
            input: sourceInput,
            id: sourceInput.getAttribute("id"),
            min: config.options.min,
            max: config.options.max,
            value: config.options.initialValue // value will be updated as the slider is moved
        };


        $.extend(config.options, options);

        // methods

        function setOrUpdateLayoutPercentages () {
            config.containerWidth = $rsContainer.outerWidth(false);
            config.sliderWidth = $slider.outerWidth(false);
            config.containerLeftOffset = $rsContainer.offset().left;
            config.containerTravelPixels = config.containerWidth - config.sliderWidth;
            config.containerTravelPercentage = (config.containerWidth - config.sliderWidth) / config.containerWidth * 100;
            config.fullRange = options.max - options.min;
            config.oneStepPixels = config.containerTravelPixels / config.fullRange;
            config.oneStepPercentage = config.containerTravelPercentage / config.fullRange;
            config.absolutePixelPointer = parseInt($sourceInput.prop("value"), 10) * config.oneStepPixels;
        }

        // Callbacks
        // The OnCreate event is called when a slider is created
        function callOnCreate () {
            if (config.options.onCreate && typeof config.options.onCreate === "function") {
                config.options.onCreate(result);
            }
        }

        // The OnStart event is called when a slider thumb has been selected
        function callOnStart () {
            if (config.options.onStart && typeof config.options.onStart === "function") {
                config.options.onStart(result);
            }
        }

        // The OnChange event is called when there is a pointerMove, a pointerUp, or a shiftOneStep event
        // If the value or position is changed programatically, there is no OnChange event
        function callOnChange () {
            if (config.options.onChange && typeof config.options.onChange === "function") {
                config.options.onChange(result);
            }
        }

        // pointerUp
        function callOnFinish () {
            if (config.options.onFinish && typeof config.options.onFinish === "function") {
                config.options.onFinish(result);
            }
        }

        function shiftOneStep (direction) {
            var currentValue = parseInt($sourceInput.prop("value"), 10);
            if (direction) {
                if (currentValue < config.options.max) {
                    currentValue += 1;
                }
            } else {
                if (currentValue > config.options.min) {
                    currentValue -= 1;
                }
            }
            $sourceInput.prop("value", currentValue);
            $slider[0].style.left = currentValue * config.oneStepPercentage + "%";
            config.absolutePixelPointer = currentValue * config.oneStepPixels;
            result.value = currentValue;
            callOnChange();
        }

        function pointerMove (event) {
            var x;
            var currentDragDistance;
            var currentPosition;
            var currentValue;
            var sliderPosition;

            /*if (!this.is_dragging) {
                window.alert("is_dragging - pointerMove");
                return;
            }*/

            x = event.pageX || (event.touches && event.touches[0].pageX);
            if (x === undefined) {
                return;
            }
            currentDragDistance = x - config.containerLeftOffset - config.fuzzyPixelPointer;
            currentPosition = currentDragDistance + config.absolutePixelPointer;
            currentValue = Math.round(currentPosition / config.oneStepPixels);

            if (currentValue < config.options.min) {
                currentValue = config.options.min;
            } else if (currentValue > config.options.max) {
                currentValue = config.options.max;
            }

            sliderPosition = currentValue * config.oneStepPercentage + "%";

            $sourceInput.prop("value", currentValue);
            $slider[0].style.left = sliderPosition;

            result.value = currentValue;

            event.preventDefault();
            callOnChange();
        }

        function pointerUp (event) {
            config.absolutePixelPointer = parseInt($sourceInput.prop("value")) * config.oneStepPixels;
            result.value = parseInt($sourceInput.prop("value"));

            doc.body.removeEventListener("pointermove", pointerMove, {passive: false});
            doc.body.removeEventListener("pointerup", pointerUp, {passive: false});
            doc.body.removeEventListener("mousemove", pointerMove, {passive: false});
            doc.body.removeEventListener("mouseup", pointerUp, {passive: false});

            $slider.trigger("focus");

            event.preventDefault();
            callOnChange();
            callOnFinish();
        }

        function pointerDown (event) {
            var x;

            if (event.button === 1 || event.button === 2) { // Only drag if the left button was clicked (on a right handed mouse)
                return;
            }

            if (win.PointerEvent) {
                // Use pointer events
                doc.body.addEventListener("pointermove", pointerMove, {passive: false});
                doc.body.addEventListener("pointerup", pointerUp, {passive: false});
            } else {
                // It's IE9 or 10 - use the mouse
                doc.body.addEventListener("mousemove", pointerMove, {passive: false});
                doc.body.addEventListener("mouseup", pointerUp, {passive: false});
            }

            x = event.pageX || (event.touches && event.touches[0].pageX);


            config.fuzzyPixelPointer = x - config.containerLeftOffset;

            event.preventDefault();
            callOnStart();
        }

        function pointerClick (event) {
            var x;
            var clickPosition;

            if (event.button === 1 || event.button === 2) {
                return;
            }
            event.preventDefault();
            x = event.pageX || (event.touches && event.touches[0].pageX);

            // if the track is clicked, figure out if the click is towards the left or right
            // of the slider, and then move one position in that direction

            //this.current_plugin = this.plugin_count;
            clickPosition = x - config.containerLeftOffset;

            if (clickPosition < config.absolutePixelPointer) { // shift left 1 step
                shiftOneStep(false);
            } else { // shift right 1 position
                shiftOneStep(true);
            }

            $slider.trigger("focus");
        }

        function keyBoard (event) {
            if (event.altKey || event.ctrlKey || event.shiftKey || event.metaKey) {
                return;
            }
            switch (event.which) {
                case 40: // DOWN
                case 37: // LEFT
                    event.preventDefault();
                    shiftOneStep(false);
                    break;

                case 38: // UP
                case 39: // RIGHT
                    event.preventDefault();
                    shiftOneStep(true);
                    break;
            }
        }

        function windowResize () {
            setOrUpdateLayoutPercentages();
        }

        plugin.update = function (value) {
            if (!sourceInput) {
                return;
            }
            if (typeof value === "string") {
                value = parseInt(value, 10);
            }
            // Set the requested position
            $sourceInput.prop("value", value);
            $slider[0].style.left = value * config.oneStepPercentage + "%";

            config.absolutePixelPointer = value * config.oneStepPixels;
        };


        // the "constructor" method that gets called when the object is created
        plugin.init = function () {
            var container_html = '<span class="rs"></span>';
            // FYI - having the tabindex made the span focusable
            var rangeSlider_html = '<span class="rs-track" tabindex="-1"></span>' +
                '<span class="rs-slider single" tabindex="' + config.tabIndex + '"></span>';

            $sourceInput.prop("value", 0); // initialize the value so the startup is consistent
            $sourceInput.before(container_html);
            $rsContainer = $sourceInput.prev();
            $rsContainer.html(rangeSlider_html);
            $track = $rsContainer.find(".rs-track");
            $slider = $rsContainer.find(".rs-slider");

            $sourceInput.prop("readonly", true);
            $sourceInput.addClass("rs-hidden-input").attr('tabindex', '-1');

            setOrUpdateLayoutPercentages();

            if (win.PointerEvent) {
                // Use pointer events
                $track[0].addEventListener("pointerdown", pointerClick, { passive: false });
                $slider[0].addEventListener("pointerdown", pointerDown, {passive: false});
            } else {
                // It's IE9 or 10 - use the mouse
                $track[0].addEventListener("mousedown", pointerClick, { passive: false });
                $slider[0].addEventListener("mousedown", pointerDown, {passive: false});
            }

            win.addEventListener("resize", windowResize, {passive: true});

            if (config.options.keyboard) {
                $track[0].addEventListener("keydown", keyBoard, {passive: false});
                $slider[0].addEventListener("keydown", keyBoard, {passive: false});
            }

            // Set the requested initial position
            $sourceInput.prop("value", config.options.initialValue);
            $slider[0].style.left = config.options.initialValue * config.oneStepPercentage + "%";

            config.absolutePixelPointer = config.options.initialValue * config.oneStepPixels;
            result.value = config.options.initialValue;

            callOnCreate();
        };

        // call the "constructor" method
        plugin.init();

    };

    // add the plugin to the jQuery.fn object
    $.fn.mtRangeSlider = function (options) {
        return this.each(function () {
            if ($.data(this, "mtRangeSlider") === undefined) {
                $.data(this, "mtRangeSlider", new mouseTouchRangeSlider(this, options));
            }
        });
    };

}(jQuery, window, document));
