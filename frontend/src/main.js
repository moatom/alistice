import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import Api from "./common/api";
import titleMixin from "./common/title";
import VueCroppie from "vue-croppie";
import "croppie/croppie.css"; // import the croppie css manually

Vue.config.productionTip = false;
Api.init();
Vue.mixin(titleMixin);

Vue.use(VueCroppie);
new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount("#app");
