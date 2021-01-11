<template>
  <v-card flat class="pa-3">
    <h1>Search</h1>
    <v-divider></v-divider>
    <div id="search">
      <bookmark-view-raw
        :username="$store.state.username"
        :ids="['']"
        :titles="['Your Bookmarks']"
        :children="children"
        :option="false"
        v-if="$store.state.username"
      />
    </div>
  </v-card>
</template>

<script>
import BookmarkViewRaw from "@/components/bookmark/BookmarkViewRaw";
import { BookmarkApi } from "@/common/api";

export default {
  props: {
    query: String
  },
  components: {
    BookmarkViewRaw
  },
  data: () => ({
    children: []
  }),
  computed: {
    titles() {
      return ["Search"];
    }
  },
  created: function() {
    BookmarkApi.search(this.query).then(({ data }) => {
      this.children = data.result;
    });
  },
  beforeRouteUpdate(to, from, next) {
    BookmarkApi.search(to.params.query).then(({ data }) => {
      this.children = data.result;
      next();
    });
  }
};
</script>
