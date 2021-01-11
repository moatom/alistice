<template>
  <v-card min-height="500" flat class="pa-5">
    <v-btn text outlined @click="toggleEdit">Edit</v-btn>
    <v-btn text outlined>Save</v-btn>
    <!-- just example -->
    <v-btn text outlined>Rule</v-btn>
    <!-- <v-divider></v-divider> -->
    <v-card outlined>
      <v-container>
        <v-row no-gutters>
          <v-col :cols="cols">
            <vue-markdown id="markdown-view" :source="source" toc />
            <!-- :anchor-attributes="anchorAttrs" -->
          </v-col>
          <v-col v-if="edit">
            <v-textarea
              name="markdown"
              label="label"
              id="markdown-editor"
              v-model="source"
              single-line
              filled
              auto-grow
              class="ml-3"
            ></v-textarea>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
    <v-btn text outlined @click="toggleEdit">Edit</v-btn>
    <v-btn text outlined>Save</v-btn>
    <v-btn text outlined>Rule</v-btn>
  </v-card>
</template>

<script>
import VueMarkdown from "vue-markdown";
export default {
  data() {
    return {
      source: "",
      // "# Notes\nYou can take a note here :-)",
      edit: false,
      cols: null,
      anchorAttrs: {
        rel: "noreferrer nofollow"
      }
    };
  },
  components: {
    VueMarkdown
  },
  mounted() {
    // source: new Date().toLocaleTimeString(),
    // setInterval(() => {
    //   this.source = new Date().toLocaleTimeString();
    // }, 1000);
    this.source = `# Notes
You can take a note here.
e.g.

---
# What is (lol)?

In this font (roboto), (lol) seems a catamorphism of a function o or bracketed lots of laugh.
However, in my opinion, (lol) is a character like  :-) 
(lol)ノ< Hello!
`;
  },
  methods: {
    toggleEdit() {
      this.edit = !this.edit;
      if (!this.cols) {
        this.cols = 6;
      } else {
        this.cols = null;
      }
    }
  }
};
</script>

<style>
#markdown-view * {
  /* all: initial !important; */
  line-height: 2 !important;
}

#markdown-view pre > code {
  /* all: initial !important; */
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
  box-sizing: border-box !important;
  overflow: auto;
  display: block;
  padding: 9.5px;
  margin: 0 0 10px;
  /* font-size: 13px; */
  color: #333;
  /* word-break: break-all;
  word-wrap: break-word; */
  background-color: #f5f5f5 !important;
  border: 1px solid #ccc !important;
  border-radius: 4px !important;
  box-shadow: none !important;
  text-indent: 0px !important;
}
#markdown-view pre > code::before {
  content: none !important;
}

#markdown-view blockquote {
  padding: 10px 20px;
  margin: 0 0 20px;
  font-size: 17.5px;
  border-left: 5px solid #eee;
}
</style>
