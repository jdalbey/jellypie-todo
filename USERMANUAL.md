## User Manual ##

Launching the application opens a simple text area for typing.  The name of the file is shown in the title bar.
Navigate using standard cursor keys and navigation buttons.
Enter each todo item on a separate line.
A scroll bar appears if there are more items than can be displayed in the text area.  The window can be resized.
<tt>Ctrl-S</tt> saves to a file. The filename is hard coded; since I don't need multiple notes there's only one file and it's in my sync folder where it will sync automatically. 
<tt>Ctrl-Q</tt> (or the window close button) will quit.

Pressing <tt>F1</tt> will present a dialog displaying the current font, the location of the config file, and the URL of this user manual.

#### Organizing Items ####
Place the cursor on an item and press <tt>Alt  \+ ↑</tt> to move it up one line,
or <tt>Alt + ↓</tt> to move it down one line.   You can press Up (or down) multiple times quickly and the item will advance in the desired direction. 

#### Adding Emphasis


| shortcut  |  effect   |
|-----------|-----|
| `Ctrl + b`  | bold    |
| `Ctrl + i`  | italic  |
| `Ctrl + t`  | fixed width|

#### Completing items ####
Place the cursor on an item and press <tt>Ctrl-d</tt> to mark it complete, which means moving it to the last line in the document and placing a "✓" character at the start of the line.  The current date and time are appended to the line.

#### Document modified status indicator ####
Whenever the application is launched it loads the specified file into the text area.
Any modification to the text will cause an asterisk to appear in the title bar. 
Saving the file clears the asterisk. 
If you attempt to quit and there are modifications, a confirmation dialog will appear prompting if you want to quit anyway, or to save and then quit.

#### Reload changes ####
If the file has been changed on disk by another process, a dialog will appear asking if you want to reload changes. 


### TYPICAL WORKFLOW ###
Just type stuff to do, one item per line.
Move high priority items to the top, low priority items to the bottom.
Mark an item done when you complete it.  View the list of completed items at the bottom of the document to see your productivity. 
Press <tt>Ctrl-S</tt> to save and then <tt>Ctrl-Q</tt> to quit.  You don't even have to release the Control key.
If you notice an item hanging around for more than a couple of days, consider moving it off the "todo" list onto a "backlog" list.  I keep a separate backlog list as a Joplin Note.  Don't clutter the "todo" list with strategic plans and long-range goals.  It's meant to be a lean and fast list of action items that need attention in the very near future, i.e., no more than a day or two. 

Some people use [these conventions](https://github.com/todotxt/todo.txt) for their todo items, but it's too hard-core for me.

### Configuration File

A configuration file is located in `~/.local/share/jellypie/config.json` containing several preference settings that you can modify to your liking.

```{
{
    "filepath": "~/jellypie_demo.todo",
    "scheme": "jellypie",
    "font_family": "Noto Sans",
    "font_size": 14,
    "font_weight": 400,
    "allow_jellypie_formatting": true,
    "shortcuts": {
        "save": "<Control>s",
        "find": "<Control>f",
        "go_to_line": "<Control>g",
        "font": "F6",
        "quick_help": "F1",
        "quit": "<Control>q"
    },
    "window_width": 664,
    "window_height": 500
}
```

The `scheme` option indicates the color scheme the application will display.  Available schemes are: Jellypie, Adwaita, Adwaita Dark, Classic, Classic Dark, Cobalt, Cobalt Light, Kate, Kate Dark, Oblivion, Solarized Dark, Solarized Light, Tango

## Keyboard Shortcuts

### File Operations

| shortcut |  effect   |
|----------|-----|
|`Ctrl + s`|    Save|
|`Ctrl + q`|    Exit|

### Moving complete lines

| shortcut |  effect   |
|----------|-----|
| `Alt + ↑`  |  Move current line (or selected lines) up|
| `Alt + ↓` |  Move current line (or selected lines) down|
|`Ctrl + d`| Mark line as "done" (move to bottom) | 

### Function keys  

| shortcut  |  effect   |
|-----------|-----|
|`F1`|  Quick Help|
|`F6`|  Select font|

### Syntax Highlighting

| shortcut  |  effect   |
|-----------|-----|
| `Ctrl + b`  | bold    |
| `Ctrl + i`  | italic  |
 | `Ctrl + t`  | fixed width|
|`Ctrl + .`| Insert emoji |

### Undo

| shortcut  |  effect   |
|-----------|-----|
|`Ctrl + z`|  Undo|
|`Shift + Ctrl + z`|   Redo|

### Clipboard Operations  
All standard. (`Ctrl + c`, `Ctrl + v`, ...) 

### Search

| shortcut  |  effect   |
|-----------|-----|
|`Ctrl + f`|   Search (find)|
|`↑`|    Select previous match|
|`↓`|    Select next match|  

### Navigation

| shortcut  |  effect   |
|-----------|-----|
 |`Ctrl + home`|     Move to beginning|
|`Ctrl + end`|      Move to end|
|`Ctrl + g`|        Goto line|
|`Ctrl + ↑`|        Move to start of previous paragraph|
|`Ctrl + ↓`|        Move to end of next paragraph|





----

*Feedback is welcome.  Developers, please contribute your enhancements to the project.*

