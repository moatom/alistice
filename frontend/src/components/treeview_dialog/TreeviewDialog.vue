<template>
  <v-btn
    text
    outlined
    max-width="90"
    min-height="40"
    small
    @click.stop="open()"
  >
    <slot></slot>
    <treeview-dialog-raw
      :tree="tree"
      @hide-dialog="dialog = false"
      v-if="dialog"
    />
  </v-btn>
</template>

<script>
import { BookmarkApi } from "@/common/api";
import TreeviewDialogRaw from "./TreeviewDialogRaw";

export default {
  components: {
    TreeviewDialogRaw
  },
  data: function() {
    return {
      dialog: false,
      tree: [],
      first: true
    };
  },
  methods: {
    open() {
      if (this.first) {
        this.init();
        this.first = false;
      } else {
        this.dialog = true;
      }
    },
    init() {
      BookmarkApi.folders().then(({ data }) => {
        this.tree = [data.root];
        this.dialog = true;
      });
    }
  }
};
</script>
