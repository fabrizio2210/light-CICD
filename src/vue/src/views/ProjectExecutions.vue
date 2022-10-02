<template>
  <div>
    <div class="executing-group">
      <button
        v-on:click="handleSubmit"
        class="btn btn-primary"
        :disabled="executing"
      >
        Run now
      </button>
      <img v-show="executing" src="../assets/loading.gif" />
    </div>
    <em v-if="executions.loading">Loading executions...</em>
    <img v-show="executions.loading" src="../assets/loading.gif" />
    <span v-if="executions.error" class="text-danger"
      >ERROR: {{ executions.error }}</span
    >
    <ul v-if="executions.executions">
      <li v-for="execution in ordered_executions" :key="execution.id">
        {{
          execution.id +
            ". Started:" +
            convertDate(execution.start_time) +
            " Duration:" +
            elapsedTimeString(execution) +
            " Status:" +
            execution.rc
        }}
        <router-link
          :to="
            '/projects/' +
              project_id +
              '/executions/' +
              execution.id +
              '/output'
          "
          >output</router-link
        >
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
    avg_size() {
      if (this.ordered_executions && this.execution_outputs) {
        let sum_size = 0;
        let execs_num = 0;
        for (const exec of this.ordered_executions) {
          if (exec.stop_time) {
            if (this.execution_outputs[exec.id]) {
              sum_size += this.execution_outputs[exec.id].output.file_bytes;
              execs_num += 1;
            }
          }
        }
        return sum_size / execs_num;
      }
      return 1;
    },
    executing() {
      return this.$store.state.executions.status.executing;
    },
    project_id() {
      return this.$route.params.project_id;
    },
    executions() {
      const project_id = this.$route.params.project_id;
      if (this.$store.state.executions.all.executions_dicts[project_id]) {
        return this.$store.state.executions.all.executions_dicts[project_id];
      } else {
        return {};
      }
    },
    execution_outputs() {
      const project_id = this.$route.params.project_id;
      if (this.$store.state.executionoutputs.all.output_dicts[project_id]) {
        return this.$store.state.executionoutputs.all.output_dicts[project_id];
      } else {
        return {};
      }
    },
    ordered_executions() {
      function compare(a, b) {
        if (a.start_time < b.start_time) {
          return -1;
        }
        if (a.start_time > b.start_time) {
          return 1;
        }
        return 0;
      }
      if (this.executions.executions) {
        return Object.values(this.executions.executions).sort(compare);
      } else {
        return Array();
      }
    }
  },
  methods: {
    handleSubmit() {
      this.submitted = true;
      const { dispatch } = this.$store;
      const project_id = this.$route.params.project_id;
      dispatch("executions/executing", { project_id });
    },
    convertDate(timestamp) {
      var myDate = new Date(timestamp * 1000);
      return myDate.toLocaleString();
    },
    elapsedTimeString(execution) {
      if (!execution.stop_time) {
        if (
          this.execution_outputs &&
          this.execution_outputs[execution.id] &&
          this.avg_size != 1
        ) {
          return (
            (
              (this.execution_outputs[execution.id].output.file_bytes * 100) /
              this.avg_size
            )
              .toFixed()
              .toString() + "%"
          );
        }
        return "Not finished yet";
      }
      var sec_num = parseInt(execution.stop_time - execution.start_time, 10);
      var hours = Math.floor(sec_num / 3600);
      var minutes = Math.floor((sec_num - hours * 3600) / 60);
      var seconds = sec_num - hours * 3600 - minutes * 60;

      if (hours < 10) {
        hours = "0" + hours;
      }
      if (minutes < 10) {
        minutes = "0" + minutes;
      }
      if (seconds < 10) {
        seconds = "0" + seconds;
      }
      return hours + ":" + minutes + ":" + seconds;
    },
    async fillOutputSize() {
      this.ordered_executions.forEach(exe => {
        const project_id = exe.project_id;
        const execution_id = exe.id;
        this.$store.dispatch("executions/get", { project_id, execution_id });
        const f_byte = 0;
        const l_byte = 0;
        this.$store.dispatch("executionoutputs/fetching", {
          project_id,
          execution_id,
          f_byte,
          l_byte
        });
      });
    }
  },
  created() {
    const project_id = this.$route.params.project_id;
    this.$store.dispatch("executions/getAll", { project_id });
  },
  mounted() {
    setInterval(this.fillOutputSize, 5000);
  }
};
</script>
