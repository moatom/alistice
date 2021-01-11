<template>
  <bookmark-view-raw
    :username="username"
    :ids="ids"
    :titles="titles"
    :children="children"
  />
</template>

<script>
import BookmarkViewRaw from "@/components/bookmark/BookmarkViewRaw";
import { BookmarkApi } from "@/common/api";

export default {
  props: {
    username: String,
    bm_id: String
  },
  components: {
    BookmarkViewRaw
  },
  data: () => ({
    ids: [],
    titles: [],
    children: []
  }),
  created: function() {
    BookmarkApi.get(this.bm_id).then(({ data }) => {
      this.ids = data.ids;
      this.titles = data.titles;
      this.children = data.children;
    });
  },
  beforeRouteUpdate(to, from, next) {
    BookmarkApi.get(to.params.bm_id)
      .then(({ data }) => {
        this.ids = data.ids;
        this.titles = data.titles;
        this.children = data.children;
        next();
      })
      .catch(() => {
        next({ path: "/" });
      });
  }
};
</script>
