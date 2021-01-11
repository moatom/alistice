<template>
  <v-app-bar color="white" app min-width="500" class="top-bar">
    <v-container fluid>
      <v-row no-gutters>
        <v-col cols="2" class="my-3">
          <v-btn text to="/" v-if="!$store.state.loading">
            <span>Alistice</span>
          </v-btn>
          <v-progress-circular indeterminate color="primary" v-else />
        </v-col>

        <v-col offset="1" cols="5" class="my-1">
          <v-form @submit.prevent="search()">
            <v-text-field
              v-model="query"
              placeholder="search"
              hide-details
              single-line
              outlined
              name="q"
              required
            ></v-text-field>
          </v-form>
        </v-col>

        <v-spacer />
        <v-col
          cols="3"
          class="my-3"
          v-if="$store.state.username === $route.params.username"
        >
          <div v-if="selected_len > 0" class="float-right">
            <treeview-dialog>
              <span class="hidden-sm-and-down" v-if="selected_len < 10"
                >move ({{ selected_len }})</span
              >
              <span class="hidden-sm-and-down" v-else>move (…)</span>
              <v-icon class="hidden-md-and-up"
                >mdi-arrange-bring-forward</v-icon
              >
            </treeview-dialog>

            <v-btn
              text
              outlined
              max-width="90"
              min-height="40"
              small
              @click="deleteNode"
            >
              <span class="hidden-sm-and-down" v-if="selected_len < 10"
                >delete ({{ selected_len }})</span
              >
              <span class="hidden-sm-and-down" v-else>delete (…)</span>
              <v-icon class="hidden-md-and-up">mdi-delete-variant</v-icon>
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-app-bar>
</template>

<script>
import TreeviewDialog from "@/components/treeview_dialog/TreeviewDialog";

export default {
  components: { TreeviewDialog },
  data: () => ({
    query: "",
    icon: null
  }),
  computed: {
    selected_len() {
      return this.$store.state.move.size;
    }
  },
  methods: {
    search: function() {
      this.$router
        .push({
          name: "search",
          params: {
            query: this.query
          }
        })
        .catch(() => {});
    },
    deleteNode() {
      if (confirm("start deleting?")) {
        this.$store.dispatch("deleteBookmarks").then(() => {
          // @fix
          window.location.assign(this.$route.path);
        });
      }
    }
  }
};
</script>
