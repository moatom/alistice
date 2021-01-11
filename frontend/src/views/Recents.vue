<template>
  <div>
    <bookmark-view-raw
      :username="username"
      :ids="['']"
      :titles="['Recents']"
      :children="children"
      :option="false"
      v-if="children"
    />
    <infinite-loading @infinite="infiniteHandler" spinner="spiral">
      <div slot="no-more"></div>
      <div slot="no-results"></div>
    </infinite-loading>
  </div>
</template>

<script>
import { BookmarkApi } from "@/common/api";
import InfiniteLoading from "vue-infinite-loading";
import BookmarkViewRaw from "@/components/bookmark/BookmarkViewRaw";

export default {
  props: {
    username: String
  },
  components: {
    InfiniteLoading,
    BookmarkViewRaw
  },
  data: function() {
    return {
      date: new Date(),
      page: 0,
      children: []
    };
  },
  methods: {
    infiniteHandler($state) {
      // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString
      // The timezone is always zero UTC offset, as denoted by the suffix "Z".
      BookmarkApi.latest(this.date.toISOString(), this.page, this.username)
        .then(({ data }) => {
          if (data.children.length) {
            this.page += 1;
            this.children.push(...data.children);
            $state.loaded();
          } else {
            $state.complete();
          }
        })
        .catch(() => $state.complete());
    }
  }
};
</script>
