<template>
  <div>
    <em v-if="projectsettings.loading">Loading settings...</em>
    <img v-show="projectsettings.loading" src="../assets/loading.gif" />
    <span v-if="projectsettings.error" class="text-danger"
      >ERROR: {{ projectsettings.error }}</span
    >
    <ul v-if="projectsettings.settings">
      <li v-for="setting in projectsettings.settings" :key="setting.name">
        <form @submit.prevent="handleSubmit(setting.name)">
          <div class="form-group">
            <label for="settingvalue">{{ setting.description + ": " }}</label>
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
    updating() {
      return this.$store.state.projectsettings.status.updating;
    },
    projectsettings() {
      const project_id = this.$route.params.project_id;
      return this.$store.state.projectsettings.all.settings_dicts[project_id];
    }
  },
  methods: {
    handleSubmit(settingname) {
      const project_id = this.$route.params.project_id;
      const settingvalue = this.projectsettings.settings[settingname].value;
      const { dispatch } = this.$store;
      if (settingname) {
        dispatch("projectsettings/updating", {
          project_id,
          settingname,
          settingvalue
        });
      }
    }
  },
  created() {
    const project_id = this.$route.params.project_id;
    this.$store.dispatch("projectsettings/getAll", { project_id });
  }
};
</script>
