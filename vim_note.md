# Commands
i - insert mode
esc - command mode

:q - quit
:q!
:w - write
:wq
:h - help!

u - step back

x - delete word at curser
dd - delete line
p - put line back (after current line)

0 - line begin
^ - line begin, no white space
$ - line end
{} - paragraph

Ctrl-F	Go forward one screen
Ctrl-B	Go backward one screen
G - Go to last line
1G - Go to first line
/xxx	Search for xxx

---
You can create a new .vimrc file in your home directory. Open the terminal and enter: ```vim ~/.vimrc```. There you can enter your various configurations. When done, you need to save the file and restart vim. To be sure which vimrc is being used, you can ask inside of vim by typing: ```:echo $MYVIMRC``` 
