export default {
  methods: {
    updateTitle(title, username) {
      if (title && username) {
        document.title = `${title} (${username}) / Alistice`;
      } else {
        document.title = `Alistice`;
      }
    }
  },
  created() {
    let { title, username } = this.$options;
    if (title && username) {
      title = typeof title === "function" ? title.call(this) : title;
      this.updateTitle(title, username);
    } else {
      this.updateTitle("", "");
    }
  }
};
