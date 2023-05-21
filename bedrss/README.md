# Author Made Bed / BedRSS

A demo app with VisJS to follow an RSS feed and plot the timestamps.

Later days can add the TV off/on feeds to the same plot.

Search Twitter for #bedrss; this project was about creating marketing /
"building in public" (before I knew the #buildinpublic hash tag), 
and demonstrating lazy development practices that anyone could follow along with
by watching a series of streams.

## Status

This app was more about minimal development practices and the series 
than technical learning.

I may have called the approach 'Pain Driven Development' and done things in the 
worst possible way, until they were too annoying then I did something about them--
I'm sure I'm not the first to have invented the term or done things this way,
but I took it to the extreme in this series of projects.

Day 1 and 2 are missing because I did this on live streams and hadn't introduced
the concept to the audience yet.

It was among the first apps I laid out in this fashion, if not the beginning.

The latest changes are in the root directory and I copied them to day-X
before I started working on a subsequent day.

## Usage

Requires visjs and some RSS feeds.

Please see the index.html files for details.

Pardon the lack of details sofar here.

## Change Log

I believe I have more detailed notes and some screenshots that I Tweeted 
and Twitch stream backs, can update this file when I've located them. 
Please excuse that.

We can make the changelog better by diffing the files.

### 2023-05-21

Added README for harlanji/dev-practice release.

### Day 6 (2021-11-16 / 2021-12-10)

Added steps and bank deposits to feed, which are CSV data instead of RSS

### Day 5 (2021-11-16)

From changes.txt:

Added link and feedLink to each item and use them together as the unique ID
of an item in the dataset. We use the update method on datasets instead
of add to take into account the IDs, and we also check if the sunrise times
already exist before adding.

### Day 4 (2021-11-15)

Added TV feed


### Day 3 (2021-11-11)

Perhaps added sunrise and a second author?


## Dev Practice

Focus:

* Making an app from scratch on live stream in the laziest possible way
* Creating a VisJS plot
* Fetching RSS feed with plain JS
* Fetching CSV data and addint it to the same plot
* Basic JS controls for loading feeds onto plot
