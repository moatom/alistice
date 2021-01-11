<template>
  <v-card flat class="pa-3">
    <h1>Login</h1>
    <v-divider></v-divider><br />
    <v-card-text>
      <v-form v-model="validLogin">
        <v-text-field
          v-model="email"
          :counter="100"
          :rules="emailRules"
          type="email"
          label="email"
          name="email"
          autocomplete="email"
          required
        ></v-text-field>
        <v-text-field
          v-model="password"
          :counter="100"
          :rules="passwordRules"
          @click:append="show = !show"
          :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
          :type="show ? 'text' : 'password'"
          label="password"
          name="password"
          autocomplete="current-password"
          required
        ></v-text-field>
      </v-form>
    </v-card-text>
    <v-divider></v-divider>
    <div class="center-text">
      <v-btn
        :disabled="!validLogin"
        @click="submitInLogin"
        color="blue darken-1"
        text
        outlined
        class="ml-2"
      >
        login
      </v-btn>
    </div>
    <br />
    <hr />
    <br />

    <h1>Create your account</h1>
    <v-divider></v-divider><br />
    <v-card-text>
      <!-- name is for completion  -->
      <v-form v-model="validSignup">
        icon
        <br />
        <div class="mb-2">
          <img
            :src="cropped"
            style="height: 48px; width: 48px; max-width: 100%; vertical-align: middle;"
          />
          <v-btn class="ml-1" text outlined @click="edit_icon = !edit_icon"
            >edit</v-btn
          >
        </div>
        <!-- @fix need to disable -->
        <div
          style="display: flex;
                  justify-content: center;
                  margin-bottom: 5px;"
          v-show="edit_icon"
        >
          <label class="croppie-btn">
            <input
              :value="input"
              style="display: none;"
              type="file"
              accept="image/*"
              @change="croppie"
            />
            <span>Select</span>
          </label>
          <span class="croppie-btn" @click="crop">Apply</span>
          <span class="croppie-btn" @click="clear">Clear</span>
          <!-- bound = false; -->
        </div>
        <vue-croppie
          ref="croppieRef"
          :enableOrientation="true"
          :enableResize="false"
          :boundary="{ width: 300, height: 300 }"
          :viewport="{ width: 200, height: 200, type: 'square' }"
          v-show="edit_icon"
        />
        <v-text-field
          v-model="email"
          :counter="100"
          :rules="emailRules"
          type="email"
          label="email"
          name="email"
          autocomplete="email"
          required
        ></v-text-field>
        <v-text-field
          v-model="username"
          :counter="15"
          :rules="usernameRules"
          label="username (unique id)"
          name="username"
          required
        ></v-text-field>
        <v-text-field
          v-model="name"
          :counter="50"
          :rules="nameRules"
          label="name (for display)"
          name="name"
          required
        ></v-text-field>
        <v-text-field
          v-model="password"
          :counter="100"
          :rules="passwordRules"
          @click:append="show = !show"
          :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
          :type="show ? 'text' : 'password'"
          label="password"
          name="password"
          autocomplete="new-password"
          required
        ></v-text-field>
      </v-form>
    </v-card-text>
    <v-divider></v-divider>
    <div class="center-text">
      Comply with
      <a :href="tosUrl" target="_blank">
        Alistice Terms of Service
      </a>
      <br />
      and
      <a :href="privacyUrl" target="_blank">
        Alistice Privacy Policy
      </a>
      <br />
      <v-btn
        :disabled="!validSignup"
        @click="submitInSignup"
        color="blue darken-1"
        text
        outlined
        class="ml-2"
      >
        Yes
      </v-btn>
    </div>
  </v-card>
</template>

<script>
import missing from "@/../public/missing.png";
import serializers from "@/common/serializer";

export default {
  name: "Login",
  mixins: [serializers],
  watch: {
    edit_icon(now) {
      if (now && !this.bound) {
        this.$nextTick(function() {
          this.initCrop();
        });
      }
    }
  },
  data() {
    return {
      tosUrl: process.env.VUE_APP_BASE_URL + "/tos",
      privacyUrl: process.env.VUE_APP_BASE_URL + "/privacy",
      input: null,
      bound: false,
      cropped: missing,
      edit_icon: false,
      show: false,
      username: "",
      name: "",
      email: "",
      password: "",
      validLogin: true,
      validSignup: true
    };
  },
  computed: {},
  methods: {
    submitInLogin() {
      this.$store.dispatch("signin", {
        email: this.email,
        password: this.password
      });
      // .catch(err => console.error(err));
    },
    submitInSignup() {
      this.$store.dispatch("signup", {
        usericon: this.cropped,
        username: this.username,
        name: this.name,
        email: this.email,
        password: this.password
      });
      // .catch(err => console.error(err));
    },
    initCrop() {
      this.$refs.croppieRef.bind({
        url: "/missing.png",
        zoom: 0.0
      });
      this.bound = true;
      this.input = null;
    },
    croppie(e) {
      var files = e.target.files || e.dataTransfer.files;
      if (!files.length) return;

      var reader = new FileReader();
      reader.onload = e => {
        this.$refs.croppieRef.bind({
          url: e.target.result,
          zoom: 0.0
        });
        this.bound = true;
      };

      reader.readAsDataURL(files[0]);
    },
    // clearして，同じのをbindしても，changeが認識されない．
    crop() {
      let options = {
        type: "base64",
        size: { width: 400, height: 400 },
        format: "png"
      };
      this.$refs.croppieRef.result(options, output => {
        this.cropped = output;
        // console.log(this.cropped);
        // console.log(this.croppieImage);
      });
    },
    clear() {
      this.cropped = missing;
      this.initCrop();
    }
  }
};
</script>

<style scoped>
.croppie-btn {
  border-radius: 8px;
  padding: 6px;
  background-color: #d3d3d3;
  font-weight: bold;
  cursor: pointer;
  margin: auto 1px;
}
</style>
