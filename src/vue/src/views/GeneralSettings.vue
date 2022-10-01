<template>
  <div>
    <h3>Settings from secure api end point:</h3>
    <em v-if="settings.loading">Loading settings...</em>
    <img v-show="settings.loading" src="../assets/loading.gif" />
    <span v-if="settings.error" class="text-danger"
      >ERROR: {{ settings.error }}</span
    >
    <ul v-if="settings.settings_dict">
      <li v-for="setting in settings.settings_dict" :key="setting.id">
        <form @submit.prevent="handleSubmit(setting.name)">
          <div class="form-group">
            <label for="settingvalue">{{
              setting.id + ". " + setting.description + ": "
            }}</label>
            <input
              type="text"
              v-on:keydown="setting.untouched = false"
              v-model="setting.value"
              :placeholder="setting.default_value"
              name="settingvalue"
              class="form-control"
            />
            <button
              class="btn btn-secondary"
              :disabled="setting.untouched || updating"
            >
              Update
            </button>
          </div>
        </form>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
  computed: {
    user() {
      return this.$store.state.authentication.user;
    },
    updating() {
      return this.$store.state.settings.status.updating;
    },
    settings() {
      return this.$store.state.settings.all;
    }
  },
  watch: {},
  methods: {
    handleSubmit(settingname) {
      //const  settingvalue = this.$store.state.settings.all.settings.find(x => x.name == settingname).value;
      //            const  settingvalue = this.settings.settings.find(x => x.name == settingname).value;
      const settingvalue = this.settings.settings_dict[settingname].value;
      const { dispatch } = this.$store;
      if (settingname) {
        dispatch("settings/updating", { settingname, settingvalue });
      }
    }
  },
  created() {
    this.$store.dispatch("settings/getAll");
  }
};
</script>
