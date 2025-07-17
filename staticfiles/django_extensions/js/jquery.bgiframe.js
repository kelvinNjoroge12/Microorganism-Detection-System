/*! Copyright (c) 2010 Brandon Aaron (http://brandon.aaron.sh/)
 * Licensed under the MIT License (LICENSE.txt).
 *
 * Version 2.1.2 - MODERNIZED FIX
 */

(function($) {
    $.fn.bgiframe = ($.browser && $.browser.msie && /msie 6\.0/i.test(navigator.userAgent) ? function(s) {
        s = $.extend({
            top     : 'auto', // auto == .currentStyle.borderTopWidth
            left    : 'auto', // auto == .currentStyle.borderLeftWidth
            width   : 'auto', // auto == offsetWidth
            height  : 'auto', // auto == offsetHeight
            opacity : true,
            src     : 'javascript:false;'
        }, s);

        return this.each(function() {
            if ($(this).children('iframe.bgiframe').length === 0) {
                var iframe = document.createElement('iframe');
                iframe.className = 'bgiframe';
                iframe.frameBorder = '0';
                iframe.tabIndex = '-1';
                iframe.src = s.src;

                var style = iframe.style;
                style.display = 'block';
                style.position = 'absolute';
                style.zIndex = '-1';

                if (s.opacity !== false) {
                    style.filter = 'Alpha(Opacity=\'0\')';
                }

                style.top = (s.top === 'auto')
                    ? 'expression(((parseInt(this.parentNode.currentStyle.borderTopWidth)||0)*-1)+\'px\')'
                    : prop(s.top);

                style.left = (s.left === 'auto')
                    ? 'expression(((parseInt(this.parentNode.currentStyle.borderLeftWidth)||0)*-1)+\'px\')'
                    : prop(s.left);

                style.width = (s.width === 'auto')
                    ? 'expression(this.parentNode.offsetWidth+\'px\')'
                    : prop(s.width);

                style.height = (s.height === 'auto')
                    ? 'expression(this.parentNode.offsetHeight+\'px\')'
                    : prop(s.height);

                this.insertBefore(iframe, this.firstChild);
            }
        });
    } : function() { return this; });

    // old alias
    $.fn.bgIframe = $.fn.bgiframe;

    function prop(n) {
        return n && n.constructor === Number ? n + 'px' : n;
    }

})((typeof window.jQuery == 'undefined' && typeof window.django != 'undefined') ? django.jQuery : jQuery);