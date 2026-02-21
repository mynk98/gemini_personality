export class GameLoop {
    constructor(updateFn, renderFn) {
        this.updateFn = updateFn;
        this.renderFn = renderFn;
        this.lastTime = 0;
        this.accumulator = 0;
        this.timeStep = 1 / 60; // Fixed 60Hz physics
    }

    start() {
        requestAnimationFrame(this.loop.bind(this));
    }

    loop(time) {
        requestAnimationFrame(this.loop.bind(this));

        const dt = (time - this.lastTime) / 1000;
        this.lastTime = time;
        this.accumulator += dt;

        // Fixed Physics Step
        while (this.accumulator >= this.timeStep) {
            this.updateFn(this.timeStep);
            this.accumulator -= this.timeStep;
        }

        // Variable Render Step
        this.renderFn(dt);
    }
}
