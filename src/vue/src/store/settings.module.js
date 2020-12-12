import { settingService } from "../services";

export const settings = {
  namespaced: true,
  state: {
    all: {},
    status : {}
  },
  actions: {
    updating({ dispatch, commit }, { settingname, settingvalue }) {
      commit("updatingRequest", { });
        settingService.update(settingname, settingvalue).then(
          setting => {
            commit("updatingSuccess", setting);
          },
          error => {
            commit("updatingFailure", error);
            dispatch("alert/error", error, { root: true});
          }
        );
      },
    getAll({ commit }) {
      commit("getAllRequest");

      settingService.getAll().then(
        settings => commit("getAllSuccess", settings["settings"]),
        error => commit("getAllFailure", error)
      );
    }
  },
  mutations: {
    updatingRequest(state) {
      state.status = { updating: true };
    },
    updatingSuccess(state, setting) {
      state.status = { updated: true };
      setting.untouched = true;
      Object.assign(state.all.settings_dict[setting.name], setting);
    },
    updatingFailure(state) {
      state.status = {};
      state.user = null;
    },
    getAllRequest(state) {
      state.all = { loading: true };
    },
    getAllSuccess(state, settings) {
      const settings_dict = {}
      settings.forEach((element) => element.untouched = true);
      settings.forEach((element) => settings_dict[element.name] = element);
      state.all = { settings_dict };
    },
    getAllFailure(state, error) {
      state.all = { error };
    }
  }
};
