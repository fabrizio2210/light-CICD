import { settingService } from "../services";

export const settings = {
  namespaced: true,
  state: {
    all: {},
    status : {}
  },
  actions: {
    updating({ dispatch, commit }, { settingname }) {
      commit("updatingRequest", { });
        settingService.update(settingname).then(
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
      state.all.settings.push(setting);
    },
    updatingFailure(state) {
      state.status = {};
      state.user = null;
    },
    getAllRequest(state) {
      state.all = { loading: true };
    },
    getAllSuccess(state, settings) {
      state.all = { settings };
    },
    getAllFailure(state, error) {
      state.all = { error };
    }
  }
};
