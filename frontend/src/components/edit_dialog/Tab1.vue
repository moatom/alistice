<template>
  <v-tab-item>
    <v-card-text>
      icon
      <br />
      <div class="mb-2">
        <img
          :src="cropped"
          style="height: 48px; width: 48px; max-width: 100%; vertical-align: middle;"
        />
        <!-- v-if="cropped" -->
        <!-- <v-icon size="48" v-else>mdi-home</v-icon> -->
        <v-btn class="ml-1" text outlined @click="edit_icon = !edit_icon"
          >edit</v-btn
        >
      </div>
      <!-- need to disable -->
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
      </div>
      <vue-croppie
        ref="croppieRef"
        :enableOrientation="true"
        :enableResize="false"
        :boundary="{ width: 300, height: 300 }"
        :viewport="{ width: 200, height: 200, type: 'square' }"
        v-show="edit_icon"
      />
      <!-- the result -->
      <!-- <button @click="crop">Crop</button> -->
      <v-form v-model="validForBasic">
        <input
          name="username"
          style="visibility: hidden; top: -100px; left: -100px;"
          autocomplete="username"
        />
        <v-text-field
          v-model="new_name"
          :counter="50"
          :rules="nameRules"
          required
          label="name"
          name="name"
        ></v-text-field>
      </v-form>
      <br />
    </v-card-text>
    <v-divider />
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="red darken-1" text outlined @click="$emit('hide-dialog')"
        >Cancel</v-btn
      >
      <v-btn
        :disabled="!validForBasic"
        color="blue darken-1"
        text
        @click="
          send1();
          $emit('hide-dialog');
        "
        outlined
        >Save</v-btn
      >
    </v-card-actions>
  </v-tab-item>
</template>

<script>
import { UserApi } from "@/common/api";
import serializers from "@/common/serializer";

export default {
  props: {
    name: { type: String, required: true },
    iconUrl: { type: String, required: true }
  },
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
      input: null,
      bound: false,
      cropped: this.iconUrl,
      edit_icon: false,
      new_name: this.name,
      validForBasic: false
    };
  },
  methods: {
    initCrop() {
      this.$refs.croppieRef.bind({
        url: this.iconUrl,
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
    crop() {
      // Options can be updated.
      // Current option will return a base64 version of the uploaded image with a size of 600px X 450px.
      let options = {
        type: "base64",
        size: { width: 400, height: 400 },
        format: "png"
      };
      this.$refs.croppieRef.result(options, output => {
        this.cropped = output;
      });
    },
    send1() {
      // default is not icon but url
      if (this.cropped === this.iconUrl) {
        UserApi.put({
          name: this.new_name
        }).then(() => {
          // @fix
          window.location.assign("/" + this.$store.state.username);
        });
      } else {
        UserApi.put({
          name: this.new_name,
          usericon: this.cropped
        }).then(() => {
          window.location.assign("/" + this.$store.state.username);
        });
      }
    },
    clear() {
      this.cropped = this.iconUrl;
      this.initCrop();
    }
  }
};
</script>
