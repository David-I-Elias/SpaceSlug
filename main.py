# main tutorial taken from https://www.youtube.com/channel/UC4L3JyeL7TXQM1f3yD6iVQQ/videos
# left of on video #


# from panda3d.core import loadPrcFile
# loadPrcFile("config/conf.prc")

# bender files can be converted to .bam( non-human readable extension of .egg) using YABEE

# conf.prc variables are found in panda3d config documentation
# can also use: " from panda3d.core import loadPrcFile
#                 loadPrcFile("config/conf.prc") "
# and have a custom prc text file where the vars are stored in the file itself
# ConfigVariableManager.getGlobalPtr().listVariables() will also list all config variables


from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import *
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerEvent
from panda3d.core import CollisionHandlerPusher
from panda3d.core import CollisionSphere, CollisionNode, CollisionPlane
from panda3d.core import Plane


confVars = """
win-size 1280 720
window-title My Game
show-frame-rate-meter True
show-scene-graph-analyzer-meter False
"""

loadPrcFileData("", confVars)


keyMap = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "weapon": False
}


def updateKeyMap(key, state):
    keyMap[key] = state



class MyGame(ShowBase):
    def __init__(self):
        super().__init__()

        # disables the default mouse camera controls
        # self.disableMouse()
        self.cam.setPos(0, -150, 35)

        self.cTrav = CollisionTraverser()
        # pusher used to keep player in frame
        self.pusher = CollisionHandlerPusher()
        # self.pusher.setHorizontal(True)
        # used to detect collisions and deal with them
        self.collisionEventHandler = CollisionHandlerEvent()

        # example of how to load multiple models into a list
        # self.teapots = []
        # for i in range(10):
        #     self.teapots.append(self.loader.loadModel("models/teapot"))
        #     self.teapots[i].setColor(0.6, 0.6, 1.0, 1.0)
        #     self.teapots[i].setPos(5 * i, 0, 0)
        #     self.teapots[i].reparentTo(self.render)

        self.player = self.loader.loadModel("my-models/X-WING")
        self.player.setColor(0.6, 0.6, 1.0, 1.0)
        self.player.setHpr(90, 180, 90)
        self.player.reparentTo(self.render)

        self.playerColliderNode = CollisionNode("player")
        self.playerColliderNode.addSolid(CollisionSphere(2, -0.6, 0, 3))
        self.playerCollider = self.player.attachNewNode(self.playerColliderNode)
        base.pusher.addCollider(self.playerCollider, self.player)
        base.cTrav.addCollider(self.playerCollider, self.pusher)
        # self.playerCollider.show()

        leftPlane = CollisionPlane(Plane((1, 0, 0), (0, 0, 0)))
        self.wallNode = CollisionNode("wall")
        self.wallNode.addSolid(leftPlane)
        wall = self.render.attachNewNode(self.wallNode)
        wall.setX(-72)
        wall.show()

        rightPlane = CollisionPlane(Plane((1, 0, 0), (0, 0, 0)))
        rightPlane.flip()
        self.wallNode = CollisionNode("wall")
        self.wallNode.addSolid(rightPlane)
        wall = self.render.attachNewNode(self.wallNode)
        wall.setX(72)
        wall.show()

        lowerPlane = CollisionPlane(Plane((0, 0, 1), (0, 0, 0)))
        self.wallNode = CollisionNode("wall")
        self.wallNode.addSolid(lowerPlane)
        wall = self.render.attachNewNode(self.wallNode)
        wall.setZ(-6)
        wall.show()

        upperPlane = CollisionPlane(Plane((0, 0, 1), (0, 0, 0)))
        upperPlane.flip()
        self.wallNode = CollisionNode("wall")
        self.wallNode.addSolid(upperPlane)
        wall = self.render.attachNewNode(self.wallNode)
        wall.setZ(80)
        wall.show()

        self.accept("w", updateKeyMap, ["up", True])
        self.accept("w-up", updateKeyMap, ["up", False])
        self.accept("s", updateKeyMap, ["down", True])
        self.accept("s-up", updateKeyMap, ["down", False])
        self.accept("a", updateKeyMap, ["left", True])
        self.accept("a-up", updateKeyMap, ["left", False])
        self.accept("d", updateKeyMap, ["right", True])
        self.accept("d-up", updateKeyMap, ["right", False])
        self.accept("space", updateKeyMap, ["weapon", True])
        self.accept("space-up", updateKeyMap, ["weapon", False])

        self.speed = 30
        self.angle = 90

        self.taskMgr.add(self.keyBindupdate, "keyBindupdate")

    def keyBindupdate(self, task):
        dt = globalClock.getDt()
        pos = self.player.getPos()

        if keyMap["left"]:
            pos.x -= self.speed * dt
            if self.angle > 45:
                self.angle -= 4
                self.player.setH(self.angle)

        if not keyMap["left"]:
            if self.angle < 90:
                self.angle += 3
                self.player.setH(self.angle)

        if keyMap["right"]:
            pos.x += self.speed * dt
            if self.angle < 135:
                self.angle += 4
                self.player.setH(self.angle)

        if not keyMap["right"]:
            if self.angle > 90:
                self.angle -= 3
                self.player.setH(self.angle)

        if keyMap["up"]:
            pos.z += self.speed * dt

        if keyMap["down"]:
            pos.z -= self.speed * dt

        if keyMap["weapon"]:
            self.projectile = self.loader.loadModel("models/misc/sphere")
            self.projectile.setScale(0.5, 0.5, 1)
            self.projectile.setPos(self.player.getPos())
            self.projectile.reparentTo(self.render)

            self.playerProjectileColliderNode = CollisionNode("player_projectile")
            self.playerProjectileColliderNode.addSolid(CollisionSphere(0.5, 0, 0.2, 1))
            self.projectileCollider = self.projectile.attachNewNode(self.playerProjectileColliderNode)
            base.cTrav.addCollider(self.projectileCollider, self.pusher)
            # base.pusher.addCollider(self.projectileCollider, self.projectile)
            # self.projectileCollider.show()

            self.trajectory = ProjectileInterval(self.projectile, duration=1, startPos=(pos.x - 1, pos.y + 3, pos.z),
                                                 startVel=(0, 0, 115))
            self.trajectory.start()

            keyMap["weapon"] = False



        self.player.setPos(pos)
        return task.cont


game = MyGame()
game.run()
