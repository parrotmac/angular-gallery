/**
 * Created by isaac on 6/13/14.
 */

    var incrementAmount = 300;
    var animationSpeed = 200;
    function responsiveCarouselArrow(direction) {
        var carouselContentWidth = 0;
        var numberOfCarouselItems = $(".rc-item-collection a").length;
        for(var i = 0; i < numberOfCarouselItems; i++) {
            carouselContentWidth += $(".rc-item-collection a")[i].clientWidth;
        }
        var currentOffset = parseInt($($(".rc-container")[0]).css("left"));
        var viewWidth = $($(".rc-mask")).width();
        incrementAmount = viewWidth*0.6;
        var overhang = carouselContentWidth - (Math.abs(currentOffset) + viewWidth);
        if(direction == 'left') {
            $($(".rc-container")[0]).animate({left: -(Math.abs(currentOffset) + (incrementAmount - Math.abs(Math.min(0, overhang - incrementAmount))))}, animationSpeed);
            //Time to move <-- that way
        } else if(direction == 'right') {
            //Time to move --> this way
            $($(".rc-container")[0]).animate({left: -(Math.max(0, Math.abs(currentOffset)-incrementAmount))}, animationSpeed);
        } else {
            console.error("You are broken");
        }
    }

    // Touch-friendly carousel script
    var previousTouchLocation = 0;
    var currentTouchCount = 0;
    var pendingEvent;

    function handleStart(evt) {
        console.log(evt);
        pendingEvent = evt;
        evt.preventDefault();
        previousTouchLocation = evt.changedTouches[0].clientX;
    }

    function handleMove(evt) {
        evt.preventDefault();
        var carouselInner = $($(".rc-container")[0]);
        var carouselOuter = $($(".rc-mask")[0]);
        var maxLeft = carouselInner[0].clientWidth - carouselOuter[0].clientWidth;

        var currentLeft = carouselInner.position().left;

        var thisTouchChange = evt.changedTouches[0].clientX;

        var rightBound = Math.min(0, currentLeft + (thisTouchChange - previousTouchLocation));

        var newLeft =  Math.min(maxLeft, Math.abs(rightBound));

        carouselInner.css("left", -newLeft);
        previousTouchLocation = thisTouchChange;
        currentTouchCount++;
        console.log("touch count:" + currentTouchCount);
    }

    function handleEnd(evt) {
        console.log("touch count:" + currentTouchCount);
        if(currentTouchCount < 2) {
            //Hacks hacks hacks hacks hacks
            document.location = pendingEvent.srcElement.offsetParent.href;
        }
        currentTouchCount = 0;
    }

    var carouselSlider = document.getElementsByClassName('rc-container')[0];
    carouselSlider.addEventListener("touchmove", handleMove, false);
    carouselSlider.addEventListener("touchstart", handleStart, false);
    carouselSlider.addEventListener("touchend", handleEnd, false);
    carouselSlider.addEventListener("touchcancel", handleEnd, false);
    carouselSlider.addEventListener("touchleave", handleEnd, false);

    //Need a function that makes sure expanding the window after scrolling to the end doesn't break the layout