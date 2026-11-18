
// ============================================================================
// AOC LE32S5760 - SMART TV ENHANCEMENT ENGINE
// 1. Chrome Emulation & Modern Web Support
// 2. Global Ad-Blocking (Banners, Popups, Video Pre-Rolls)
// 3. Forced 480p Default Quality for Video Apps
// 4. Modern JavaScript & HTML5 Polyfills
// ============================================================================

(function() {
    'use strict';

    // --- 1. CHROME USER-AGENT & IDENTITY SPOOFING (Skip TV/HbbTV Portals) ---
    var host = (location && location.hostname) ? location.hostname.toLowerCase() : '';
    var isTvPortal = /nettvservices|corio|philips|tpvision|hbbtv|localhost|127\.0\.0\.1/.test(host);
    if (!isTvPortal) {
        var CHROME_UA = "Mozilla/5.0 (Linux; Android 9; SmartTV Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36";
        var APP_VER = "5.0 (Linux; Android 9; SmartTV Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36";
        try {
            Object.defineProperty(navigator, 'userAgent', { get: function() { return CHROME_UA; }, configurable: true });
            Object.defineProperty(navigator, 'appVersion', { get: function() { return APP_VER; }, configurable: true });
            Object.defineProperty(navigator, 'vendor', { get: function() { return "Google Inc."; }, configurable: true });
            Object.defineProperty(navigator, 'vendorSub', { get: function() { return ""; }, configurable: true });
            Object.defineProperty(navigator, 'productSub', { get: function() { return "20030107"; }, configurable: true });
        } catch(e) {
            try {
                if (navigator.__defineGetter__) {
                    navigator.__defineGetter__('userAgent', function() { return CHROME_UA; });
                    navigator.__defineGetter__('appVersion', function() { return APP_VER; });
                    navigator.__defineGetter__('vendor', function() { return "Google Inc."; });
                }
            } catch(e2) {}
        }
        try {
            window.chrome = window.chrome || {
                app: { isInstalled: false },
                runtime: { OnInstalledReason: {}, OnRestartRequiredReason: {} },
                loadTimes: function() { return { requestTime: Date.now() / 1000 }; },
                csi: function() { return { startE: Date.now() }; }
            };
        } catch(e3) {}
    }

    // --- 2. GLOBAL AD-BLOCKING INJECTION (Safe Explicit Ad Selectors Only) ---
    function injectAdblockCSS() {
        if (!document.head && !document.documentElement) return;
        var style = document.createElement('style');
        style.type = 'text/css';
        style.textContent = ''
            + '.video-ads, .ytp-ad-module, .ytp-ad-overlay-container, .ytp-ad-player-overlay, '
            + '.ad-container, .advertisement, #ad-banner, .banner-ad, '
            + 'iframe[src*="doubleclick.net"], iframe[src*="googlesyndication.com"], iframe[src*="adnxs.com"], '
            + '.tv-ad-banner, .smart-ad, #portal-ad-box, .nettv-ad-banner, .ad_unit, '
            + '.ad-slot, .sponsored-post, .sponsor-box, [data-ad-slot] { '
            + '    display: none !important; '
            + '    visibility: hidden !important; '
            + '    width: 0 !important; '
            + '    height: 0 !important; '
            + '    pointer-events: none !important; '
            + '} ';
        (document.head || document.documentElement).appendChild(style);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectAdblockCSS, false);
    } else {
        injectAdblockCSS();
    }

    // Auto-skip pre-roll and mid-roll video advertisements
    setInterval(function() {
        try {
            var skipBtn = document.querySelector('.ytp-ad-skip-button, .ytp-ad-skip-button-modern, .videoAdUiSkipButton');
            if (skipBtn && typeof skipBtn.click === 'function') {
                skipBtn.click();
            }
            var adVideo = document.querySelector('.ad-showing video, video.ad-interrupting');
            if (adVideo && !isNaN(adVideo.duration) && isFinite(adVideo.duration) && adVideo.duration > 0) {
                adVideo.currentTime = adVideo.duration;
            }
        } catch(e) {}
    }, 800);

    // --- 3. FORCE 480P QUALITY ACROSS ALL VIDEO PLAYBACK APPS ---
    try {
        localStorage.setItem('yt-player-quality', JSON.stringify({
            data: "480p",
            expiration: Date.now() + 315360000000,
            creation: Date.now()
        }));
        localStorage.setItem('yt-player-sticky-quality', JSON.stringify({
            data: "480p"
        }));
        localStorage.setItem('yt-player-av-sticky-quality', JSON.stringify({
            data: "480p"
        }));
    } catch(e) {}

    // Hook HTML5 Video Elements
    if (window.HTMLVideoElement && HTMLVideoElement.prototype) {
        var origPlay = HTMLVideoElement.prototype.play;
        HTMLVideoElement.prototype.play = function() {
            this.setAttribute('data-target-resolution', '480p');
            return origPlay.apply(this, arguments);
        };
    }

    // Clamp YouTube / SmartTV Video Player Objects to 480p (Large/Medium)
    function clampPlayerTo480p(p) {
        if (!p) return;
        try {
            if (typeof p.setPlaybackQualityRange === 'function') {
                p.setPlaybackQualityRange('medium', 'large');
            }
            if (typeof p.setPlaybackQuality === 'function') {
                p.setPlaybackQuality('large'); // 480p standard in YouTube API
            }
        } catch(e) {}
    }

    setInterval(function() {
        if (window._yt_player) {
            for (var key in window._yt_player) {
                if (window._yt_player[key] && typeof window._yt_player[key].setPlaybackQuality === 'function') {
                    clampPlayerTo480p(window._yt_player[key]);
                }
            }
        }
        var moviePlayer = document.getElementById('movie_player');
        if (moviePlayer && typeof moviePlayer.setPlaybackQuality === 'function') {
            clampPlayerTo480p(moviePlayer);
        }
    }, 1000);

    // --- 4. MODERN JS POLYFILL SUITE (ES6+, Promise, Fetch, Object, Array) ---
    if (typeof Object.assign !== 'function') {
        Object.assign = function(target) {
            if (target === null || target === undefined) throw new TypeError('Cannot convert undefined or null to object');
            var to = Object(target);
            for (var i = 1; i < arguments.length; i++) {
                var nextSource = arguments[i];
                if (nextSource !== null && nextSource !== undefined) {
                    for (var nextKey in nextSource) {
                        if (Object.prototype.hasOwnProperty.call(nextSource, nextKey)) {
                            to[nextKey] = nextSource[nextKey];
                        }
                    }
                }
            }
            return to;
        };
    }

    if (typeof Object.entries !== 'function') {
        Object.entries = function(obj) {
            var res = [];
            for (var k in obj) {
                if (Object.prototype.hasOwnProperty.call(obj, k)) res.push([k, obj[k]]);
            }
            return res;
        };
    }
    if (typeof Object.values !== 'function') {
        Object.values = function(obj) {
            var res = [];
            for (var k in obj) {
                if (Object.prototype.hasOwnProperty.call(obj, k)) res.push(obj[k]);
            }
            return res;
        };
    }

    if (!Array.prototype.includes) {
        Array.prototype.includes = function(searchElement, fromIndex) {
            var O = Object(this);
            var len = parseInt(O.length, 10) || 0;
            if (len === 0) return false;
            var n = parseInt(fromIndex, 10) || 0;
            var k = n >= 0 ? n : Math.max(0, len + n);
            while (k < len) {
                if (searchElement === O[k] || (searchElement !== searchElement && O[k] !== O[k])) return true;
                k++;
            }
            return false;
        };
    }
    if (!Array.prototype.find) {
        Array.prototype.find = function(predicate) {
            for (var i = 0; i < this.length; i++) {
                if (predicate(this[i], i, this)) return this[i];
            }
            return undefined;
        };
    }
    if (!Array.prototype.findIndex) {
        Array.prototype.findIndex = function(predicate) {
            for (var i = 0; i < this.length; i++) {
                if (predicate(this[i], i, this)) return i;
            }
            return -1;
        };
    }
    if (!Array.from) {
        Array.from = function(object) {
            return [].slice.call(object);
        };
    }

    if (!String.prototype.includes) {
        String.prototype.includes = function(search, start) {
            if (typeof start !== 'number') start = 0;
            if (start + search.length > this.length) return false;
            return this.indexOf(search, start) !== -1;
        };
    }
    if (!String.prototype.startsWith) {
        String.prototype.startsWith = function(search, pos) {
            return this.substr(!pos || pos < 0 ? 0 : +pos, search.length) === search;
        };
    }
    if (!String.prototype.endsWith) {
        String.prototype.endsWith = function(search, this_len) {
            if (this_len === undefined || this_len > this.length) this_len = this.length;
            return this.substring(this_len - search.length, this_len) === search;
        };
    }

    if (!window.requestAnimationFrame) {
        window.requestAnimationFrame = function(callback) {
            return setTimeout(function() { callback(Date.now()); }, 1000 / 60);
        };
        window.cancelAnimationFrame = function(id) {
            clearTimeout(id);
        };
    }

    if (typeof window.Promise !== 'function') {
        var PENDING = 0, FULFILLED = 1, REJECTED = 2;
        function SimplePromise(executor) {
            var state = PENDING;
            var value = null;
            var handlers = [];

            function fulfill(result) {
                if (state !== PENDING) return;
                state = FULFILLED;
                value = result;
                if (handlers) handlers.forEach(handle);
                handlers = null;
            }

            function reject(error) {
                if (state !== PENDING) return;
                state = REJECTED;
                value = error;
                if (handlers) handlers.forEach(handle);
                handlers = null;
            }

            function resolve(result) {
                try {
                    var then = typeof result === 'object' && result !== null ? result.then : null;
                    if (typeof then === 'function') {
                        then.call(result, resolve, reject);
                        return;
                    }
                    fulfill(result);
                } catch(e) {
                    reject(e);
                }
            }

            function handle(handler) {
                if (state === PENDING) {
                    handlers.push(handler);
                } else {
                    setTimeout(function() {
                        var cb = state === FULFILLED ? handler.onFulfilled : handler.onRejected;
                        if (typeof cb !== 'function') {
                            (state === FULFILLED ? handler.resolve : handler.reject)(value);
                            return;
                        }
                        try {
                            handler.resolve(cb(value));
                        } catch(e) {
                            handler.reject(e);
                        }
                    }, 0);
                }
            }

            this.then = function(onFulfilled, onRejected) {
                return new SimplePromise(function(res, rej) {
                    handle({ onFulfilled: onFulfilled, onRejected: onRejected, resolve: res, reject: rej });
                });
            };

            this['catch'] = function(onRejected) {
                return this.then(null, onRejected);
            };

            try {
                executor(resolve, reject);
            } catch(e) {
                reject(e);
            }
        }
        SimplePromise.resolve = function(val) { return new SimplePromise(function(res) { res(val); }); };
        SimplePromise.reject = function(err) { return new SimplePromise(function(res, rej) { rej(err); }); };
        SimplePromise.all = function(promises) {
            return new SimplePromise(function(res, rej) {
                var results = [], count = 0;
                if (!promises || promises.length === 0) { res(results); return; }
                promises.forEach(function(p, i) {
                    SimplePromise.resolve(p).then(function(val) {
                        results[i] = val;
                        count++;
                        if (count === promises.length) res(results);
                    }, rej);
                });
            });
        };
        window.Promise = SimplePromise;
    }

    if (typeof window.fetch !== 'function') {
        window.fetch = function(url, options) {
            options = options || {};
            return new Promise(function(resolve, reject) {
                var xhr = new XMLHttpRequest();
                xhr.open(options.method || 'GET', url, true);
                if (options.headers) {
                    for (var h in options.headers) {
                        xhr.setRequestHeader(h, options.headers[h]);
                    }
                }
                xhr.onload = function() {
                    resolve({
                        ok: xhr.status >= 200 && xhr.status < 300,
                        status: xhr.status,
                        statusText: xhr.statusText,
                        text: function() { return Promise.resolve(xhr.responseText); },
                        json: function() {
                            try { return Promise.resolve(JSON.parse(xhr.responseText)); }
                            catch(e) { return Promise.reject(e); }
                        }
                    });
                };
                xhr.onerror = function() { reject(new TypeError('Network request failed')); };
                xhr.ontimeout = function() { reject(new TypeError('Network request timed out')); };
                xhr.send(options.body || null);
            });
        };
    }
})();


opera.postError("Opera HbbTV user JS loading ..");

// Add onreadystatechange for XMLHttpRequests
(function() {
	var tmpInstance=new XMLHttpRequest();// because Opera doesn't support getter/setter lookup on prototype
	var orscGetter=tmpInstance.__lookupGetter__('onreadystatechange');
	var orscSetter=tmpInstance.__lookupSetter__('onreadystatechange');
	XMLHttpRequest.prototype.__defineGetter__('onreadystatechange', function(){
		return orscGetter.call(this);
	});
	XMLHttpRequest.prototype.__defineSetter__('onreadystatechange', function( actualListener ){
		var intermediateListener = function(){
		     if (typeof(actualListener) === "function")
			actualListener.call(this, {target: this});
		}
		return orscSetter.call(this, intermediateListener);
	});
})();


// fix for yahoo back key. given by opera PR 165381
opera.addEventListener("BeforeEventListener.keydown", function (ev)
{
	if (location.hostname.indexOf('yahoo') > -1) 
	{
	   if (ev.event.keyCode == 8)
       {
            ev.preventDefault();
       }
     }
}, false);


// Set overflow:hidden needs to be done on both <html> and <body>
window.addEventListener('load', function() {
	if (getComputedStyle(document.getElementsByTagName('body')[0], null).overflow == 'hidden') {
		document.getElementsByTagName('html')[0].style.overflow = 'hidden';
	}
}, false);


// Patch for Redmine issue #1246
if (location.hostname.indexOf('hbbtv.ndr.de') != -1) {
	opera.addEventListener('BeforeScript', function(e) {
		e.element.text = e.element.text.replace("startFallbackUrl: 'dvb://current.ait/13.1B?autoshow=1", "startFallbackUrl: 'dvb://current.ait/13.1?autoshow=1");
	}, false);
}


// Patch for issues in jQuery 1.6.2 related to operations on innerHTML within an XML context (HSDK-1522).
if (location.hostname.indexOf('json.bild.de') != -1) {
	opera.addEventListener('BeforeScript', function(e) {
		if (e.element.src.indexOf('jquery1.6.2.min.js') != -1) {
			e.element.text = e.element.text.replace('o.innerHTML=m[1]+k+m[2];', 'try{o.innerHTML=m[1]+k+m[2];}catch(e){};');
		}
	}, false);
}

//France24 JIT crash fix
if (location.href.indexOf('philips.playintv.com/portal/france24/') != -1)
{
    window.opera.addEventListener('BeforeScript', function (e)
    {
        var frameworkRegexp = new RegExp('Framework.prototype.getLanguage');

        if (frameworkRegexp.test(e.element.text))
            e.element.text = e.element.text.replace('if(this.language==null){}', '');

    }, false);
}

//BBC trick mode keys fix
if (location.hostname.indexOf('bbc.co.uk') != -1 && location.hostname.indexOf('incubator') == -1)
{
        opera.addEventListener('BeforeEvent.load', function(e)
        {
                if (!(e.event.target instanceof Document)) return;
                if (typeof(window.antie) == "undefined") return;
	        opera.postError("bbc.co.uk iplayer input map userjs");
		function updateMap(map, update) {
			for (var key in update) {
				if (!map.hasOwnProperty(key)) {
					map[key] = update[key];
				}
			}
		}
		updateMap(window.antie.framework.deviceConfiguration["input"]["map"],
			{"19":"PAUSE", "412":"REWIND", "413":"STOP", "415":"PLAY", "417":"FAST_FWD","457": "INFO","403":"RED","404":"GREEN","405":"YELLOW","406":"BLUE"});
        }, null);
}

//DASH fix, from browser.js, for consistency with Philips integration
if (!window.URL){
    window.URL = {
        createObjectURL: function(x) {
            return x;
        }
    };
}

//PDSTR7-305
if (location.hostname.indexOf('.google.') != -1) {
    window.addEventListener('load', function() {
        if (document.getElementById("gbqfqw")) {
            document.getElementById("gbqfqw").onkeyup = function(e) {
                if (e.keyCode == 13) {
                    document.getElementById("gbqfq").focus();
                }
            }
        }
    });
}

if (location.hostname.indexOf('mail.google.com') >= 0) {
	console.log(location);
	if (location.search.indexOf('ui=html') < 0) {
		if (location.search.indexOf('?') >= 0) {
			location.search = location.search + '&ui=html';
		} else {
			location.search = location.search + '?ui=html';
		}
	}
}

// RIDER4-87
if (document.location.href.indexOf('google.com') != -1)
{
    opera.addEventListener('AfterEvent.load', function(e)
    {
        var all = document.getElementsByClassName("gbqfba gbqfba-hvr");

        if(all && all[0] && all[0].childNodes && all[0].childNodes[0].childNodes)
        {
            var l = all[0].childNodes[0].childNodes;
            var len = l.length;
            for(var i=0; i<len-1; i++)
                l[0].parentNode.removeChild(l[0]);
        }
    }, false);
}

//TF515PHILTMTK00-261
if (document.location.href.indexOf('facebook.com') != -1)
{
    opera.addEventListener('AfterEvent.load', function(e)
    {
        var div1 = document.getElementsByClassName("_5o0-");

        for (var i=0; i<div1.length; i++)
        {
        	if (div1[i].parentNode.className.indexOf('_5o0z') != -1)
        	{
        		if (div1[i].parentNode.parentNode.className.indexOf('_5o0y') != -1)
	        	{
	        		div1[i].parentNode.parentNode.parentNode.removeChild(div1[i].parentNode.parentNode);
	        	}
        	}
        }

    }, false);
}

//ebay menu navigation fix
if (location.hostname.indexOf('ebay.com') != -1) {
        opera.addEventListener('BeforeScript', function(e) {
	  if (e.element.src.indexOf('gr5dd42clizvdk4tyqdabpcvw.js') != -1) {
	    e.element.text = e.element.text.replace(/;t\.timer=window\.setTimeout\(vjo\.hitch\(t,function\(\){/g, ';t.timer=window.setTimeout(vjo.hitch(t,function(){return;');  //remove changing spatnav confusion
	    e.element.text = e.element.text.replace(/hpce:function\(t\){/g, 'hpce:function(t){ document.activeElement.style.outlineStyle="none"; ');	//remove outline if hide submenu
	    e.element.text = e.element.text.replace(/l\[i\+d\]\.focus\(\)/g, '{ document.activeElement.style.outlineStyle="none"; l[i+d].focus(); l[i+d].style.outlineStyle="solid"; l[i+d].style.outlineWidth="1"; l[i+d].style.outlineColor="#3091f2";}'); //remove old outline and add new otline for focused element
	    e.element.text = e.element.text.replace(/case 39:/g, 'break; case 39:'); //fixed navigation in menu
	    e.element.text = e.element.text.replace(/case 40:/g, 'case 40: if(document.activeElement.parentNode.tagName != "H2")'); //fixed navigation in menu
	    e.element.text = e.element.text.replace(/case 38:/g, 'case 38: if(document.activeElement.parentNode.tagName != "H2")'); //fixed navigation in menu
	  }
        }, false);
}

//RIDER4-41 Fix for BBC iPlayer flickering problem
//Fix for new version of iPlayer
if (location.hostname.indexOf('bbc.co.uk') != -1) {
	var css = '#episodeInfoImageOverlayBlack { background-color: black; width: 100%; height: 100%; position: absolute; top: 0; left: 0; }',head = document.getElementsByTagName('head')[0],style = document.createElement('style');
	style.type = 'text/css'; if (style.styleSheet){style.styleSheet.cssText = css;} else {style.appendChild(document.createTextNode(css));}head.appendChild(style);

	opera.addEventListener('BeforeScript', function(e) {
		e.element.text = e.element.text.replace('this._image.appendChildWidget(new b("episodeInfoImageOverlay"));','this._image.appendChildWidget(new b("episodeInfoImageOverlayBlack"));this._image.appendChildWidget(new b("episodeInfoImageOverlay"));');
		e.element.text = e.element.text.replace('this._imageElement=m.createImage(this.id+"_img",null,this._src,this._size);', 'var funLoaded = undefined; if(this.id === "episodeInfoImage") { funLoaded = function() { setTimeout(function (){ document.getElementById("episodeInfoImageOverlayBlack").style.visibility="hidden" }, 250);} } this._imageElement=m.createImage(this.id+"_img",null,this._src,this._size,funLoaded);');
	}, false);
}

//RIDER4-57 Fix for YouTube thumbnails cropped
if (document.location.href.indexOf('youtube.com') > -1) {
	opera.addEventListener('BeforeScript', function(e){
		str = e.element.text;
		if (e.element.src.indexOf('app-prod.js') > -1) {
			str = str.replace(
				'a.css("background-image","url("+this.src+")")}',
				'a.css("background-image","url("+this.src+")");a.next().text(a.next().text());}'
			);
		}
		e.element.text = str;
	},false);
}

//RIDER4-88 & RIDER4-123 Force www.skype.com to not use svg
if (location.hostname.indexOf('skype.') != -1) {
    opera.addEventListener('BeforeScript', function(e) {
        if (e.element.src.indexOf('skype.min.js') != -1)
            e.element.text = e.element.text.replace('var a=!!document.createElementNS&&!!document.createElementNS("http://www.w3.org/2000/svg","svg").createSVGRect;', 'var a=false;');
        else if (e.element.src.indexOf('modernizr.js') != -1)
            e.element.text = e.element.text.replace('return!!b.createElementNS&&!!b.createElementNS(r.svg,"svg").createSVGRect', 'return false');
    }, false);
}

//RIDER4-119 & RIDER4-185
if ((location.href.indexOf('nettvacc.corio.com') != -1) || (location.href.indexOf('sp-test1-origin.portal.nettvservices.com') != -1) || (location.href.indexOf('nettv.corio.com') != -1))
{
	window.opera.addEventListener("BeforeEvent.keypress", function (evt) {
		var keypress = evt.event;  // the keypress event
		if(keypress.keyCode == keypress.charCode && (
		//disable exclamation mark `!` keypress, because it is mistakenly handled like page up button in Philips SmatrTv portal in search field
		keypress.keyCode == 33 ||
		//disable quotation mark `"` keypress, because it is mistakenly handled like page down button in Philips SmatrTv portal in search field
		keypress.keyCode == 34 ||
		//disable percent sign `%` keypress, because it is mistakenly handled like left button in Philips SmatrTv portal in search field
		keypress.keyCode == 37 ||
		//disable ampersand `&` keypress, because it is mistakenly handled like up button in Philips SmatrTv portal in search field
		keypress.keyCode == 38 ||
		//disable apostrophe `'` keypress, because it is mistakenly handled like right button in Philips SmatrTv portal in search field
		keypress.keyCode == 39 ||
		//disable left parenthesis `(` keypress, because it is mistakenly handled like down button in Philips SmatrTv portal in search field
		keypress.keyCode == 40)) 
			keypress.stopPropagation();
  });
}

//RIDER4-112 focus language button after closing language selection pop-up 
if ((location.hostname.indexOf('euronews.net') != -1) || (location.hostname.indexOf('euronews.com') != -1))
{
	opera.addEventListener('BeforeScript', function(e) {
		if (e.element.src.indexOf('main.js') != -1) {
		  e.element.text = e.element.text.replace("mainObj.changeLang($(this).attr('href').replace(\"#\", \"\"));", "mainObj.changeLang($(this).attr('href').replace(\"#\", \"\")); document.getElementById('navLang').focus();");
		}
	}, false);
}

