<template>
  <v-card flat class="pa-3">
    <h1>Import</h1>
    <v-divider></v-divider><br /><br />
    <v-file-input
      type="file"
      accept=".html"
      label="File input"
      color="blue"
      counter
      placeholder="Select your bookmark file"
      outlined
      :show-size="1000"
      @change="getFileContent"
      v-model="filePath"
    >
    </v-file-input>

    <v-dialog v-model="dialog" width="600px">
      <template v-slot:activator="{ on }">
        <div class="center-text">
          <v-btn
            :disabled="!content"
            text
            outlined
            v-on="on"
            @click="parse()"
            class="ml-2"
            color="blue darken-1"
            >send</v-btn
          >
        </div>
      </template>

      <v-card>
        <v-card-title>
          <span class="headline">Select folders</span>
        </v-card-title>
        <v-card-text>
          <!-- https://ej2.syncfusion.com/vue/documentation/treeview/drag-and-drop/ -->
          <v-treeview
            v-model="tree"
            :open="open"
            :items="filtered.children"
            selectable
            item-key="id"
            item-text="title"
            open-on-click
          >
            <template v-slot:prepend="{ item, open }">
              <v-icon v-if="item.type === 'folder'">
                {{ open ? "mdi-folder-open" : "mdi-folder" }}
              </v-icon>
            </template>
          </v-treeview>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="red darken-1" outlined text @click="dialog = false"
            >Cancel</v-btn
          >
          <v-btn
            :disabled="tree.length < 1"
            color="blue darken-1"
            text
            @click="
              dialog = false;
              injectNodes(parsed);
            "
            outlined=""
            >Import</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import parser from "node-bookmarks-parser";
import tree from "@/common/tree";
import { BookmarkApi } from "@/common/api";

export default {
  data: function() {
    return {
      overlay: false,
      content: null,
      parsed: {
        type: "folder",
        title: "stacked",
        addDate: null,
        lastModified: null,
        nsRoot: "stacked",
        children: []
      },
      dialog: false,
      tree: [],
      open: [],
      filtered: {},
      filePath: null,
      bmCnt: 0
    };
  },
  mounted() {},
  computed: {
    hasContent: function() {
      return this.content.keys.length < 1;
    }
  },
  methods: {
    async getFileContent(file) {
      if (file) {
        try {
          const content = await this.readFileAsync(file);
          this.content = content;
        } catch (e) {
          window.alert("failed in reading the file");
        }
      } else {
        this.content = null;
      }
    },
    readFileAsync(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          resolve(reader.result);
        };
        reader.onerror = reject;
        reader.readAsText(file);
      });
    },
    addId(node) {
      if (node.type === "folder") {
        node.id = this.bmCnt++;
        node.children.forEach(e => this.addId(e));
      }
    },
    parse: function() {
      try {
        this.parsed.children = parser(this.content);
        this.bmCnt = 0;
        this.addId(this.parsed);
        this.filtered = tree.cutLeaf(JSON.parse(JSON.stringify(this.parsed)));
      } catch (e) {
        // console.error(e);
      }
    },
    selectNodes: function(node, targets) {
      if (tree.filterByFolder(node).every(e => this.tree.includes(e))) {
        targets.push(node);
      } else {
        node.children
          .filter(e => e.type === "folder")
          .forEach(element => {
            this.selectNodes(element, targets);
          });
      }
    },
    injectNodes: function(node) {
      let targets = [];
      this.selectNodes(node, targets);
      let root = {};
      if (targets.length === 1 && targets[0].nsRoot === "stacked") {
        root = targets[0];
      } else {
        root = {
          type: "folder",
          title: "temp_root",
          addDate: null,
          lastModified: null,
          nsRoot: "draft_root",
          children: targets
        };
      }
      this.$store.state.loading = true;
      BookmarkApi.add(root)
        .then(() => {
          this.content = null;
          this.filePath = null;
          this.$store.state.loading = false;
          window.alert("Imported");
        })
        .catch(() => {
          this.$store.state.loading = false;
        });
      this.content = null;
    }
  }
};
</script>
