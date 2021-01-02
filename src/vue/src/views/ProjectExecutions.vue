<template>
    <div>
        <div class="executing-group">
            <button v-on:click="handleSubmit" class="btn btn-primary" :disabled="executing" >Run now</button>
            <img v-show="executing" src="../assets/loading.gif" />
        </div>
        <em v-if="executions.loading">Loading executions...</em>
        <img v-show="executions.loading" src="../assets/loading.gif" />
        <span v-if="executions.error" class="text-danger">ERROR: {{executions.error}}</span>
        <ul v-if="executions.executions">
            <li v-for="execution in executions.executions" :key="execution.id">
                {{execution.id + '. Started:' + execution.start_time + ' Status:' + execution.rc}}
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    data () {
        return {
        }
    },
    computed: {
        executing () {
            return this.$store.state.executions.status.executing;
        },
        executions () {
            const project_id = this.$route.params.project_id;
            return this.$store.state.executions.all.executions_dicts[project_id];
        }
    },
    methods: {
        handleSubmit () {
            this.submitted = true;
            const { dispatch } = this.$store;
            const project_id = this.$route.params.project_id;
            dispatch('executions/executing', { project_id });
        }
    },
    created () {
        const project_id = this.$route.params.project_id;
        this.$store.dispatch('executions/getAll', { project_id });
    }
};
</script>
