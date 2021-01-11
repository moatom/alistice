const tree = {
  cutLeaf: function(node) {
    node.children = node.children
      .filter(e => e.type === "folder")
      .map(e => this.cutLeaf(e));
    return node;
  },
  filterByFolder: function(node) {
    let t = node.children.filter(e => e.type === "folder");
    if (t.length < 1) {
      return [node.id];
    }
    return t.flatMap(e => this.filterByFolder(e));
  }
};

export default tree;
