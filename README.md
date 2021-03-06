# tarkov-deploy

tarkov-deploy can do the following:

* Watch the screen for a "Deploying in:" message, and sound a warning notification when detected
* Watch the screen for an invite confirmation, and automatically pressing "y" if the person is in the approved list of folks to auto-accept invites

## Installation

This project required Tesseract OCR to also be installed on the machine. This is the software that takes an image (screenshot that tarkov-deploy captures) and detects the text. Windows builds can be found here:  https://github.com/UB-Mannheim/tesseract/wiki

After that, simply go to the [latest release](https://github.com/blitzmann/tarkov-deploy/releases/latest) and download and extract the zip file. Poke around the `config.json` file to set any configuration you may want, and run the exe.

## Caveats

This project works by finding the Tarkov window, and taking a screenshot of what that window reports as it's position and size. If there are any programs in front of the Tarkov window, they will be part of the screenshot and thus throw off the results. Because of this, using a multi-monitor setup is ideal

The auto-accept functionality will focus the window before clicking "Y" - if you're working on another project on another screen, this will take focus away from it.

There are probably better ways to do this, but this was quick and easy. 

There is no error handling. it just stops if it runs into an error (which is probably often)

PRs welcome!

## Configuration

Please see the the `config.json` file for configuration options

## Why?

Originally I just wanted something to warn me that our team was deploying. Because of the amazingly variable match and wait times before you deploy in Tarkov, oftentimes I would step away from the computer to get a chore done, grab a snack, etc. Because BSG hasn't implemented a notification themselves, I wanted something to let me know to haul ass back to the computer instead of relying on teammates to mention it in Discord

As for auto-accepting invites, same deal. Oftentimes I'm in lobby before my teammates, and step away form the computer. Just wanted to make sure I'm not holding up the team.
