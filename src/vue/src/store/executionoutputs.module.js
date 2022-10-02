import { executionoutputService } from "../services";
import Vue from "vue";

export const executionoutputs = {
  namespaced: true,
  state: {
    all: { output_dicts: {} },
    status: {}
  },
  actions: {
    fetching(
      { dispatch, commit },
      { project_id, execution_id, f_byte, l_byte }
    ) {
      commit("fetchingRequest", {});
      executionoutputService.get(project_id, execution_id, f_byte, l_byte).then(
        output => {
          commit("fetchingSuccess", { output, project_id, execution_id });
        },
        error => {
          commit("fetchingFailure", error);
          dispatch("alert/error", error, { root: true });
        }
      );
    }
  },
  mutations: {
    fetchingRequest(state) {
      state.status = { fetching: true };
    },
    fetchingSuccess(state, p) {
      state.status = { fetched: true };
      !(p.project_id in state.all.output_dicts) &&
        Vue.set(state.all.output_dicts, p.project_id, {});
      !(p.execution_id in state.all.output_dicts[p.project_id]) &&
        Vue.set(state.all.output_dicts[p.project_id], p.execution_id, {});
      if (Object.keys(state.all.output_dicts[p.project_id][p.execution_id]).length != 0){
        Vue.set(
          state.all.output_dicts[p.project_id][p.execution_id]["output"],
          "file_bytes",
          p.output["output"]["file_bytes"]
        );
        if (p.output["output"]["last_transmitted_byte"] > state.all.output_dicts[p.project_id][p.execution_id]["output"]["last_transmitted_byte"]) {
          Vue.set(
            state.all.output_dicts[p.project_id][p.execution_id]["output"],
            "data",
            p.output["output"]["data"]
          );
          Vue.set(
            state.all.output_dicts[p.project_id][p.execution_id]["output"],
            "first_transmitted_byte",
            p.output["output"]["first_transmitted_byte"]
          );
        }
      } else {
        Vue.set(
          state.all.output_dicts[p.project_id][p.execution_id],
          "output",
          p.output["output"]
        );
      }
      state.status = {};
    },
    fetchingFailure(state) {
      state.status = {};
      state.user = null;
    }
  }
};
