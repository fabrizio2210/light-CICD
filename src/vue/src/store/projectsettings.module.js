import { projectsettingService } from "../services";
import Vue from "vue";

export const projectsettings = {
  namespaced: true,
  state: {
    all: { settings_dicts : {} },
    status : {}
  },
  actions: {
    updating({ dispatch, commit }, { project_id, settingname, settingvalue }) {
      commit("updatingRequest", { });
        projectsettingService.update(project_id, settingname, settingvalue).then(
          setting => {
            commit("updatingSuccess", { setting, project_id });
          },
          error => {
            commit("updatingFailure", error);
            dispatch("alert/error", error, { root: true});
          }
        );
      },
    getAll({ commit }, { project_id }) {
      commit("getAllRequest",  project_id );
      projectsettingService.getAll(project_id).then(
        settings => commit("getAllSuccess", { settings, project_id }),
        error => commit("getAllFailure", error)
      );
    }
  },
  mutations: {
    updatingRequest(state) {
      state.status = { updating: true };
    },
    updatingSuccess(state, p) {
      var setting = p.setting["setting"];
      var project_id = p.project_id;
      state.status = { updated: true };
      setting.untouched = true;
      Vue.set(state.all.settings_dicts[project_id]['settings'], setting.name, setting);
    },
    updatingFailure(state) {
      state.status = {};
      state.user = null;
    },
    getAllRequest(state, project_id) {
      Vue.set(state.all.settings_dicts, project_id, { loading: true });
    },
    getAllSuccess(state, p) {
      var settings = p.settings["settings"];
      var project_id = p.project_id;
      settings.forEach(function(element) {
        element.untouched = true;
        !(project_id in state.all.settings_dicts) && (Vue.set(state.all.settings_dicts, project_id, {}));
        !('settings' in state.all.settings_dicts[project_id]) && (Vue.set(state.all.settings_dicts[project_id], 'settings', {}));
         Vue.set(state.all.settings_dicts[project_id]['settings'], element.name, element);
      });
      Vue.delete(state.all.settings_dicts[project_id], 'loading');
    },
    getAllFailure(state, error) {
      state.all = { error };
    }
  }
};
