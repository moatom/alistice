<template>
  <!-- これに対するcreatedを呼びたい apiの呼び出しはそのままに，ここだけv-ifで別コンポーネント化するべき．-->
  <v-dialog
    v-model="dialog"
    @click:outside="$emit('hide-dialog')"
    width="600px"
    scrollable
  >
    <!-- contents サイズを変えないで，スクロールの設定に・・・-->
    <v-card>
      <v-card-title>
        <span class="headline">Select a folder</span>
      </v-card-title>
      <v-text-field
        v-model="search"
        label="Search Directory"
        hide-details
        single-line
        outlined
        clearable
        class="mx-6 mb-2"
        name="dirs"
      ></v-text-field>
      <v-divider />
      <v-card-text class="mt-2">
        <v-treeview
          open-all
          v-model="selected"
          :open.sync="open"
          :items="tree"
          :search="search"
          selectable
          item-key="id"
          item-text="title"
          open-on-click
          selection-type="independent"
          @input="keepOne"
        >
          <template v-slot:prepend="{ item, open }">
            <v-icon>
              {{ open ? "mdi-folder-open" : "mdi-folder" }}
            </v-icon>
          </template>
        </v-treeview>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="red darken-1"
          text
          @click="
            dialog = false;
            $emit('hide-dialog');
          "
          outlined
          >Cancel</v-btn
        >
        <v-btn
          :disabled="selected.length < 1"
          color="blue darken-1"
          outlined
          text
          @click="
            dialog = false;
            $emit('hide-dialog');
            move();
          "
          >Select</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
// cancel時に初期化したい
// initでは？
export default {
  props: {
    tree: Array
  },
  data: function() {
    return {
      dialog: true,
      selected: [], //selected nodes
      open: [],
      // dest_id: null,
      search: null,
      all_id: [],
      first_for_open: true
    };
  },
  watch: {
    open(newVal) {
      if (this.first_for_open) {
        this.all_id = newVal;
        this.first_for_open = false;
        this.open = [];
      }
    },
    search(newVal) {
      if (newVal) {
        this.open = this.all_id;
      } else {
        this.open = [];
      }
    }
  },
  mounted() {},
  computed: {
    dest_id() {
      return this.selected[0];
    }
  },
  methods: {
    move() {
      if (confirm("start moving?")) {
        this.$store.dispatch("moveBookmarks", this.dest_id).then(() => {
          // @fix
          window.location.assign(this.$route.path);
        });
      }
    },
    keepOne(value) {
      this.selected = [value[value.length - 1]];
    }
  }
};
</script>
