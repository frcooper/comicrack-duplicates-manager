# ![Duplicates Manager](docs/images/duplicatesmanager-2.png) `                     `  DUPLICATES MANAGER FOR [COMICRACK](https://github.com/maforget/ComicRackCE) #

---

## NEW VERSION 0.9 ##

### Updated  with NEW RULES, see the [rules page](docs/RulesFileSyntax.md) ###

```
v0.9 -> 

   Added:    - New rules: 
                    - scan keep/remove
             - New toolbar icon
             - Fix for typos and rare crash
```
[Complete CHANGELOG](docs/Changelog.md)

---


### IMPORTANT NOTICE (UPDATED AS OF VERSION 0.5) ###
Since I do not want to mess with your files & library before we are sure this thing works right,
|**the script out of the box will not move or remove any comic, just log what it would do in the logfile. To enable the actual processing of files you need to  add the values  true for the variables `MOVEFILES` and `REMOVEFROMLIB`** in the **dmrules.dat** file. See the [Configuration Options](docs/UserConfiguration.md) page for details.|
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|


---


This script is an addon to comicrack that identifies duplicated ecomics and follows a set of user defined rules to remove unwanted dupes. It is designed with the 0-days in mind, but should prove useful in other scenarios.

The script reads a file (**dmrules.dat**) from the directory where it is installed, that contains, both user options, and a series of rules to manage the duplicate files. Duplicate files that meet the criteria expressed in the rules are **moved** to a dump directory (not deleted) and removed from the comicrack library (default dump directory is `C:\_dupes_`). This directory also holds a logfile (**logfile.log**) that details the process followed on your comics

So, the first thing you want to do is read the rules (see [Rules Syntax](docs/RulesFileSyntax.md)) and edit your custom **dmrules.dat** file.

Documentation:

  * [Overview](docs/Overview.md): You need to read this first!!!!
  * Rules are explained in detail in [Rules Syntax](docs/RulesFileSyntax.md).
  * Then you can go to the [Tips and Examples](docs/TipsAndTricks.md) page.
  * User defined variables are described in the [Configuration Options](docs/UserConfiguration.md)  page.
  * Credits for people who have (not necessary knowingly) contributed to this project in [the credits](docs/FellowCredits.md) page
  * Screenshot and example files at [this page](docs/ScreenshotExample.md)
  * Changelog is in [this other page](docs/Changelog.md)

Discussion is provided in the [comicrack support forum (archived)](https://web.archive.org/web/20161013114923/http://comicrack.cyolito.com/forum/13-scripts/12076-duplicates-manager)


---


Cheers!!!!! ![perezmu](https://web.archive.org/web/20151228182417id_/http://comicrack.cyolito.com/media/kunena/avatars/resized/size72/users/avatar195.jpg)