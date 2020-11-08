<template>
    <div>
        <form @submit.prevent="handleSubmit">
            <div class="form-group">
                <label for="projectname">Project Name</label>
                <input type="text" v-model="projectname" name="projectname" class="form-control" :class="{ 'is-invalid': submitted && !projectname }" />
                <div v-show="submitted && !projectname" class="invalid-feedback">Project Name is required</div>
            </div>
            <div class="form-group">
                <button class="btn btn-primary" :disabled="creating" >New Project</button>
                <img v-show="creating" src="../assets/loading.gif" />
            </div>
        </form>
        <h3>Projects from secure api end point:</h3>
        <em v-if="projects.loading">Loading projects...</em>
        <img v-show="projects.loading" src="../assets/loading.gif" />
        <span v-if="projects.error" class="text-danger">ERROR: {{projects.error}}</span>
        <ul v-if="projects.projects">
            <li v-for="project in projects.projects" :key="project.id">
                {{project.id + '. ' + project.name}}
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    data () {
        return {
            projectname: '',
            submitted: false
        }
    },
    computed: {
        user () {
            return this.$store.state.authentication.user;
        },
        creating () {
            return this.$store.state.projects.status.creating;
        },
        projects () {
            return this.$store.state.projects.all;
        }
    },
    methods: {
        handleSubmit () {
            this.submitted = true;
            const { projectname } = this;
            const { dispatch } = this.$store;
            if (projectname) {
                dispatch('projects/creating', { projectname });
            }
        }
    },
    created () {
        this.$store.dispatch('projects/getAll');
    }
};
</script>
