from nose.tools import eq_
from nose.tools import raises
import unittest


def test_cache_control_object_max_age_None():
    from webob.cachecontrol import CacheControl
    cc = CacheControl({}, 'a')
    cc.properties['max-age'] = None
    eq_(cc.max_age, -1)


class TestUpdateDict(unittest.TestCase):

    def setUp(self):
        self.call_queue = []
        def callback(args):
            self.call_queue.append("Called with: %s" % repr(args))
        self.callback = callback

    def make_one(self, callback):
        from webob.cachecontrol import UpdateDict
        ud = UpdateDict()
        ud.updated = callback
        return ud
    
    def test_set_delete(self):
        newone = self.make_one(self.callback)
        newone['first'] = 1
        assert len(self.call_queue) == 1
        assert self.call_queue[-1] == "Called with: {'first': 1}"        

        del newone['first'] 
        assert len(self.call_queue) == 2
        assert self.call_queue[-1] == 'Called with: {}'                

    def test_setdefault(self):
        newone = self.make_one(self.callback)
        assert newone.setdefault('haters', 'gonna-hate') == 'gonna-hate'
        assert len(self.call_queue) == 1
        assert self.call_queue[-1] == "Called with: {'haters': 'gonna-hate'}", self.call_queue[-1]

        # no effect if failobj is not set
        assert newone.setdefault('haters', 'gonna-love') == 'gonna-hate'
        assert len(self.call_queue) == 1

    def test_pop(self):
        newone = self.make_one(self.callback)
        newone['first'] = 1
        newone.pop('first')
        assert len(self.call_queue) == 2
        assert self.call_queue[-1] == 'Called with: {}', self.call_queue[-1]                

    def test_popitem(self):
        newone = self.make_one(self.callback)
        newone['first'] = 1
        assert newone.popitem() == ('first', 1)
        assert len(self.call_queue) == 2
        assert self.call_queue[-1] == 'Called with: {}', self.call_queue[-1]                

    def test_callback_args(self):
        assert True
        #assert False


class TestExistProp(unittest.TestCase):
    """
    Test webob.cachecontrol.exists_property
    """
    
    def setUp(self):
        pass

    def make_one(self):
        from webob.cachecontrol import exists_property

        class Dummy(object):
            properties = dict(prop=1)
            type = 'dummy'
            prop = exists_property('prop', 'dummy')
            badprop = exists_property('badprop', 'big_dummy')
            
        return Dummy

    def test_get_on_class(self):
        from webob.cachecontrol import exists_property
        Dummy = self.make_one()
        assert isinstance(Dummy.prop, exists_property), Dummy.prop

    def test_get_on_instance(self):
        obj = self.make_one()()
        assert obj.prop is True

    @raises(AttributeError)
    def test_type_mismatch_raise(self):
        obj = self.make_one()()
        obj.badprop = True

    def test_set_w_value(self):
        obj = self.make_one()()
        obj.prop = True
        assert obj.prop is True
        assert obj.properties['prop'] is None

    def test_del_value(self):
        obj = self.make_one()()
        del obj.prop
        assert not 'prop' in obj.properties


class TestValueProp(unittest.TestCase):
    """
    Test webob.cachecontrol.exists_property
    """
    
    def setUp(self):
        pass

    def make_one(self):
        from webob.cachecontrol import value_property

        class Dummy(object):
            properties = dict(prop=1)
            type = 'dummy'
            prop = value_property('prop', 'dummy')
            badprop = value_property('badprop', 'big_dummy')
            
        return Dummy

    def test_get_on_class(self):
        from webob.cachecontrol import value_property
        Dummy = self.make_one()
        assert isinstance(Dummy.prop, value_property), Dummy.prop

    def test_get_on_instance(self):
        dummy = self.make_one()()
        assert dummy.prop, dummy.prop 
        #assert isinstance(Dummy.prop, value_property), Dummy.prop

    def test_set_on_instance(self):
        dummy = self.make_one()()
        dummy.prop = "new"
        assert dummy.prop == "new", dummy.prop
        assert dummy.properties['prop'] == "new", dict(dummy.properties)

    def test_set_on_instance_w_default(self):
        dummy = self.make_one()()
        dummy.prop = "dummy"
        assert dummy.prop == "dummy", dummy.prop
        #@@ this probably needs more tests

    def test_del(self):
        dummy = self.make_one()()
        dummy.prop = 'Ian Bicking likes to skip'
        del dummy.prop
        assert dummy.prop == "dummy", dummy.prop


def test_copy_cc():
    from webob.cachecontrol import CacheControl
    cc = CacheControl({'header':'%', "msg":'arewerichyet?'}, 'request')
    cc2 = cc.copy()
    assert cc.properties is not cc2.properties
    assert cc.type is cc2.type

# 212    

def test_serialize_cache_control():
    from webob.cachecontrol import serialize_cache_control, CacheControl
    serialize_cache_control(dict())
    # properties, type
    serialize_cache_control(CacheControl({}, 'request'))

    serialize_cache_control(CacheControl({'header':'%'}, 'request'))
