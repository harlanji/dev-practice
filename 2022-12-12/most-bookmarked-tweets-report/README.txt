Top 25 most influential Tweeters of 2022 and prior,

Of 250 users bookmarked in 5,690 Tweets:

1.  ...

This report was built with data from my personal apps. 

Stay tuned for my engagement report where I cound my number of Retweets for the same users--
my equivalent to the Like button. Maybe next year the notes app will have date limited searches.
As my capabilities and wisdom evolve my approach to social media will follow.

Thanks.

Code to build this report is included in the upcoming verson of The Notes App.

https://harlanji.gumroad.com/l/the-notes-app

```
notesAppUrl = 'http://localhost:5000'


temp1 = await fetch(notesAppUrl + '/notes/cards/search?q=twitter.com/').then(r => r.json())

re = /(https?[a-z0-9\.\/\:]+twitter\.com\/[0-9a-z\_]+\/status\/[\d]+)/ig

cardMatches = temp1.cards
    .map(cm => Object.assign({}, cm, {tweetLinks: Array.from(new Set(cm.card.content.match(re)))}))
    .filter(cm => cm.tweetLinks && cm.tweetLinks.length)
    .map(cm => Object.assign({}, cm, {tweetUrls: cm.tweetLinks.map(l => new URL(l))}))
    .map(cm => Object.assign({}, cm, {tweetInfos: cm.tweetUrls.map(u => ({user: u.pathname.split('/')[1], tweetId: u.pathname.split('/')[3]}))}));

tweetsByUser = cardMatches.reduce(function (report, m) {
  m.tweetInfos.forEach(function (ti) {
    if (!(ti.user in report)) {
      report[ti.user] = [];
    }
    report[ti.user].push(ti);
  });
  return report;
}, {});

tweetsById = cardMatches.reduce(function (report, m) {
  m.tweetInfos.forEach(function (ti) {
    if (!report[ti.tweetId]) {
      report[ti.tweetId] = [];
    }
    report[ti.tweetId].push(ti);
  });
  return report;
}, {});

top25Authors = Object.entries(tweetsByUser).sort(function (a, b) { return b[1].length - a[1].length }).slice(0,25)

console.log("Top 25 authors:")
console.log(top25Authors.map((e, i) => `${i+1}.\t@${e[0]}: ${e[1].length}` ).join("\n"))

console.log("Total tweets: " + Object.keys(tweetsById).length);
```
