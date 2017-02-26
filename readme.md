# ScreenBloom

A Flask application to parse a screen's average color and send the value to connected <a href="http://www2.meethue.com/en-us/">Philips Hue Bulbs</a>.

![No Man's Sky with ScreenBloom](https://thumbs.gfycat.com/MixedPertinentAtlanticbluetang-size_restricted.gif)

####More info at <a href="http://www.screenbloom.com">screenbloom.com</a>

<hr>

##Docs / Help
* **[Settings](#settings)**
* **[Presets](#presets)**
* **[Performance Tips](#performance)**
* **[Command Line Args](#cli)**
* **[API](#api)**
* **[Developers](#devs)**

<hr>

<a name="settings">
###Settings
Basic explanations of the various editable settings within ScreenBloom.

* **Global Brightness** sets a hard limit for how bright or how dim ScreenBloom will be able to tune your lights.  Each light has its own min/max brightness settings, but the global value will always take priority.  Dynamic brightness can effectively be turned off by setting the min and max values equal to each other.

* **Update Speed** contains two settings: **Update Buffer** and **Transition Speed**
  * **Update Buffer** sets a small delay in between update loops.  This feature was introduced to address a problem with various CPUs running the ScreenBloom update loop inconsistently, potentially leading to large delays as the Hue bridge becomes overwhelmed with commands.  This setting can provide a huge speedup on older hardware.
  * **Transition Speed** maps to the Hue API value for the speed of the color transition animation.  Lower values will seem more responsive while higher values will be smoother.

* **Chose Display** is a Windows-only feature allowing you to set which display ScreenBloom will parse.

* **Party Mode** sends a random RGB color to each of your selected bulbs using your chosen transition speed.  Kind of outside the scope of ScreenBloom but I wanted the functionality and added it on a whim a few years ago.

* **Screen Zones** will divide up the screen into discrete ScreenBloom-parsable zones.  A common use case is to split the screen in half and assign each half to a light on either side of the room/TV/monitor.

* **Bulbs** is where you select or de-select lights to be included in the ScreenBloom update loop.

* **Saturation** arbitrarily enhances the the color ScreenBloom parses to be more vibrant and saturated.  Uses <a href="http://pillow.readthedocs.io/en/3.1.x/reference/ImageEnhance.html#PIL.ImageEnhance.Color">this method</a> of <a href="http://pillow.readthedocs.io/en/3.1.x/">PIL/Pillow</a>.

* **Auto Start** determines if the ScreenBloom update loop starts automatically after the program is launched.

<hr>

<a name="presets">
###Presets 
![ScreenBloom Presets Button](http://www.screenbloom.com/static/images/presets.png)

Saving a preset gathers up all your current settings, including selected bulbs and their individual settings, and saves them as a preset.  Presets can be updated by expanding their options menu and clicking **Update**, which overrides the preset with the current ScreenBloom settings.

<hr>

<a name="performance">
###Performance Tips
ScreenBloom can be extremely responsive but there are a number of factors that will contribute to how well it performs.

* **Hardware**.  ScreenBloom will run on pretty much anything but you're going to have the best results on a relatively modern quad-core system.  There's a pretty wide difference in performance between my beefy desktop gaming PC and my 2014 Macbook Pro, for instance.

* **Network**.  You'll get the best results on a PC with a stable, wired connection.  Routers configurations and firewalls can also play a role, but I don't have a lot of data about that to say definitively.

* **Number of displays**.  The more connected displays, the more pixel data ScreenBloom has to parse, adding to the overall processing time.  Often this slight increase (milliseconds) isn't a huge deal, but to get the absolute best performance from ScreenBloom you will want to consider disabling displays that aren't currently in use.  Windows 10 makes this a very simple process (right click desktop -> Display Settings).  I've found a great program that allows you to set profiles, very handy: **<a href="https://sourceforge.net/projects/monitorswitcher/">Monitor Profile Switcher</a>**.

* **Number of lights**.  Each light that ScreenBloom addresses during its update loop adds another 2-4 commands that must be processed by the Hue bridge before continuing on to the next set of commands (I.E. the next light).  Philips recommends a budget of ~10 commands per second to prevent bridge congestion, which means the more lights being addressed the higher potential for congestion / slowdown.  I think the sweet spot is around 5 lights, with 1 light giving the best possible performance and anything under 10 giving pretty acceptable performance.

* **Update Buffer**.  If you're on older hardware or are generally experiencing large delays between ScreenBloom light updates, consider experimenting with the **Update Buffer** setting (located in the **Update Speed** section).

<hr>

<a name="cli">
###Command Line Args (Windows version)

On Windows, ScreenBloom can be launched with command line arguments.  This functionality is limited to just silent mode at the moment, I hope to expand it in the future.

* **Silent Mode**. use the `-q` or `--silent` commands to launch ScreenBloom without opening a browser to the web interface.  If you have autostart enabled the ScreenBloom update loop will begin.

<hr>

<a name="api">
###API
Though it wasn't really designed for it from the outset, ScreenBloom is fully addressable and scriptable as a RESTful API.

Endpoints should be pretty easy to discern from the main <a href="https://github.com/kershner/screenBloom/blob/master/app/screenbloom.py">screenbloom.py</a> file, starting after the index() function.

Requests can be sent to the ScreenBloom web server:

`http://<screenbloom_webserver_host>:<screenbloom_webserver_port>/endpoint`

Example to **start** ScreenBloom update loop:

`[GET] http://192.168.0.69:5000/start`

**POST** endpoints accept their parameters in JSON format and will return a JSON response.  Take a look at the individual endpoint functions to figure out the exact format it expects.

<hr>

<a name="devs">
###Developers
Forks and pull requests very welcome!  Don't hesitate to contact me or raise an issue if you have any questions.

For convenience/organization I've bundled the vendor files ScreenBloom uses:

###<a href="http://kershner.org/static/distribute/sb_2.2_vendor_files.zip">ScreenBloom Vendor Files</a>
