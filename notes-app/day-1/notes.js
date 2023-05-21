
// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
function debounce(func, wait, immediate) {
        var timeout;
        return function() {
                var context = this, args = arguments;
                var later = function() {
                        timeout = null;
                        if (!immediate) func.apply(context, args);
                };
                var callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func.apply(context, args);
        };
};


function WebDavFileSystem(baseUrl) {
  this.baseUrl = baseUrl || "/storage";
}

WebDavFileSystem.prototype.list = function list(path) {
  var baseUrl = this.baseUrl;

  var url = baseUrl + path;



  return fetch(url, {method: "PROPFIND"})
    .then(function (r) { return r.text(); })
    .then(function (str) { return new window.DOMParser().parseFromString(str, "text/xml"); })
    .then(function (r) {
      console.log(r);
      var items = r.querySelectorAll("multistatus response");
      items = Array.prototype.slice.call(items);
      items = items.map(function (i) {
        var i = {
          path: i.querySelector("href").textContent,
          created_at: i.querySelector("prop creationdate").textContent,
          modified_at: i.querySelector("prop getlastmodified").textContent,
          length_bytes: i.querySelector("prop getcontentlength").textContent,
          display_name: i.querySelector("prop displayname").textContent,
          status: i.querySelector("status").textContent
        };

        if (i.path) {
          i.path = i.path.substr(baseUrl.length);
        }

        return i;
      });



      return items;
    });


}

WebDavFileSystem.prototype.upload = function upload(path, contentType, content) {
  var url = this.baseUrl + path;
  return fetch(url, {method: 'PUT', body: content});
}

WebDavFileSystem.prototype.download = function download(path) {
  var url = this.baseUrl + path;
  return fetch(url)
    .then(function (r) { return r.text(); })
}


var fs = new WebDavFileSystem();

var notesStore;


function saveNote() {
  // post note to /upload
  // post new .csv to /upload (logic should be on server)
}

function syncNotesFromDir() {
  fs.list("/").then(function (files) {
    var IDs = files.filter(function (f) {
      return f.path.endsWith(".txt");
    });

    var data = IDs.map(function (id) {
      return [id.path, id.created_at, id.modified_at];
    })
    console.log(data);
    //notesStore.clear();
    notesStore.loadData(data, true);
  });
}
var notesStore = new Ext.data.SimpleStore({
  fields: ["id", "created", "modified", "title", "body", "attachment_keys"],
  id: 0,
  data: []
});
notesStore.on("add", function (store, records, idx) {
  console.log("Notes added: ");
  console.log(records);
  var noteNodes = records.map(noteToNode);
  var notesFolders = Ext.ComponentMgr.get("notesFolders");
  var notesNode = notesFolders.root;
  notesNode.appendChild(noteNodes);
});

function noteToNode(record) {
  var title = record.data.id;
  var node = new Ext.tree.TreeNode({
    text: title,
    leaf: true,
    noteId: record.data.id
  });
  return node;
}



function  runNotesApp () {
    Ext.QuickTips.init();
    var viewport = Ext.getCmp('viewport');

    var win;
    var selectedNoteId = null;
    if (!win) {
      var noteNodes = notesStore.getRange().map(noteToNode);
      var notesNode = new Ext.tree.TreeNode({
        text: "Notes",
        expanded: true
      });
      notesNode.appendChild(noteNodes);

      function addHandler() {
        var newId = "/note-" + Math.random() + ".txt";
        var date = new Date().toString();
        newId = prompt("ID for new note:", newId);
        // this should be the effect of a dispatch.
        fs.upload(newId, "text/plain", "").then(function () {

          notesStore.loadData([
            [newId, date, date]
          ], true);
          var note = notesStore.getById(newId);
          //notesNode.appendChild(noteToNode(note));
        });
      }
      var foldersComp = {
        xtype: "treepanel",
        id: "notesFolders",
        tbar: [{
          text: 'Add',
          handler: addHandler
        }],
        root: notesNode,
        listeners: {
          click: function (node, evt) {
            var id = node.attributes.noteId;
            var editor = Ext.ComponentMgr.get("noteEditor");
            selectedNoteId = id; // includes deselect, eg. folder.
            if (!id) {
              editor.setValue("");
              return;
            }
            console.log("note click: " + id);
            var note = notesStore.getById(id);
            //var noteHtml = note.data.body;
            fs.download( note.data.id ).catch(function (err) {
              console.log("error: " + err.httpStatus);
            }).then(function (noteHtml) {
              var editor = Ext.ComponentMgr.get("noteEditor");
              editor.setValue(noteHtml);
            });
          }
        }
      };
      var foldersConfig = {
        region: "west",
        split: true,
        width: 160,
        layout: "fit",
        border: false,
        items: [foldersComp]
      };
      var noteConfig = {
        region: "center",
        split: true,
        border: false,
        layout: "border",
        items: [{
          region: "center",
          xtype: "htmleditor",
          html: "Note.",
          id: "noteEditor",
          border: false
        }, {
          region: "south",
          border: false,
          html: "Note stats."
        }]
      };
      var searchConfig = {
        xtype: "textfield",
        width: 150,
        emptyText: "Search..."
      };
      win = new Ext.Panel({
        tbar: [{
          xtype: "tbspacer"
        }, searchConfig],
        id: "notes-win",
        header: false,
        title: "Notes",
        layout: "border",
        bodyBorder: false,
        autoShow: true,
        //border: false,
        //height: 280,
        //width: 460,
        items: [foldersConfig, noteConfig],
        //bbar: []
      });
    }

    viewport.add(win);
    viewport.doLayout();
    //win.show();
    //win.maximize();

    syncNotesFromDir();
    var editor = Ext.ComponentMgr.get("noteEditor");
    editor.on("sync", debounce(function (e, html) {
      console.log("Editor sync. Selected = " + selectedNoteId);
      if (!selectedNoteId) {
        return;
      }
      var note = notesStore.getById(selectedNoteId);
      fs.upload(note.data.id, "text/plain", html);
      //note.beginEdit();
      //note.set("body", html);
      //note.endEdit();
    }, 750));
}
